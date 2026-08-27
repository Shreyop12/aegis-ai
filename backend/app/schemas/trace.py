from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TraceCreate(BaseModel):
    application: str = Field(min_length=1, max_length=100)
    environment: Literal["development", "staging", "production"]

    model: str = Field(min_length=1, max_length=100)

    user_input: str = Field(min_length=1)
    prompt: str = Field(min_length=1)

    model_output: str | None = None

class TraceCreated(BaseModel):
    trace_id: UUID
    status: Literal["accepted"]