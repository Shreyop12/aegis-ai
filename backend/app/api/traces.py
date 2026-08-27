from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.trace import Trace
from backend.app.schemas.trace import TraceCreate, TraceCreated

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