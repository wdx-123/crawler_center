from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..config import settings


class UserRequest(BaseModel):
    username: str = Field(min_length=1)
    sleep_sec: float = Field(default=settings.DEFAULT_SLEEP_SEC, ge=0.0, le=10.0)


class LuoguUserRequest(BaseModel):
    uid: int = Field(gt=0)
    sleep_sec: float = Field(default=settings.DEFAULT_SLEEP_SEC, ge=0.0, le=10.0)


class OkResponse(BaseModel):
    ok: bool = True
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
