from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        ser_json_timedelta="iso8601",
    )


class ErrorResponse(BaseSchema):
    detail: str
    code: str


class HealthResponse(BaseSchema):
    status: str
    timestamp: datetime
