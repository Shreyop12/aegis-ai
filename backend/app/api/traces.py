from uuid import uuid4

from fastapi import APIRouter, status

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
async def create_trace(trace: TraceCreate) -> TraceCreated:
    trace_id = str(uuid4())

    return TraceCreated(
        trace_id=trace_id,
        status="accepted",
    )