from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.trace import Trace
from backend.app.schemas.trace import (
    TraceCreate,
    TraceCreated,
    TraceListResponse,
    TraceRead,
    TraceSummary,
)

router = APIRouter(
    prefix="/v1/traces",
    tags=["traces"],
)


@router.post(
    "",
    response_model=TraceCreated,
    status_code=status.HTTP_201_CREATED,
)
def create_trace(
    trace: TraceCreate,
    db: Session = Depends(get_db),  # noqa: B008
) -> TraceCreated:
    db_trace = Trace(
        application=trace.application,
        environment=trace.environment,
        model=trace.model,
        user_input=trace.user_input,
        prompt=trace.prompt,
        model_output=trace.model_output,
    )

    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)

    return TraceCreated(
        trace_id=db_trace.id,
        status="accepted",
    )

@router.get(
    "",
    response_model=TraceListResponse,
)
def list_traces(
    db: Session = Depends(get_db),  # noqa: B008
    application: str | None = None,
    environment: Literal[
        "development",
        "staging",
        "production",
    ]
    | None = None,
    model: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TraceListResponse:
    statement = select(Trace)

    if application is not None:
        statement = statement.where(Trace.application == application)

    if environment is not None:
        statement = statement.where(Trace.environment == environment)

    if model is not None:
        statement = statement.where(Trace.model == model)

    statement = (
    statement.order_by(
        Trace.created_at.desc(),
        Trace.id.desc(),
    )
    .limit(limit)
    .offset(offset)
)

    traces = db.scalars(statement).all()

    items = [
        TraceSummary(
            trace_id=trace.id,
            application=trace.application,
            environment=trace.environment,
            model=trace.model,
            created_at=trace.created_at,
        )
        for trace in traces
    ]

    return TraceListResponse(
        items=items,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{trace_id}",
    response_model=TraceRead,
)
def get_trace(
    trace_id: UUID,
    db: Session = Depends(get_db),  # noqa: B008
) -> TraceRead:
    db_trace = db.get(Trace, trace_id)

    if db_trace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found",
        )

    return TraceRead(
        trace_id=db_trace.id,
        application=db_trace.application,
        environment=db_trace.environment,
        model=db_trace.model,
        user_input=db_trace.user_input,
        prompt=db_trace.prompt,
        model_output=db_trace.model_output,
        created_at=db_trace.created_at,
    )