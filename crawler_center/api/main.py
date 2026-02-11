from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from ..leetcode_client import LeetCodeClient
from ..leetcode_types import format_local_time
from ..luogu_client import LuoguClient
from .schemas import ErrorResponse, LuoguUserRequest, OkResponse, UserRequest


app = FastAPI(title="crawler_center", version="0.1.0")

# 第一个异常处理-处理所有HTTPException类型错误
@app.exception_handler(HTTPException)
def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=str(exc.detail)).model_dump(),
    )

# 兜底异常处理
@app.exception_handler(Exception)
def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error=str(exc)).model_dump(),
    )


@app.get("/healthz", response_model=OkResponse)
def healthz() -> OkResponse:
    return OkResponse(data={"status": "ok"})


def _get_client(sleep_sec: Optional[float] = None) -> LeetCodeClient:
    if sleep_sec is not None:
        return LeetCodeClient(sleep_sec=sleep_sec)
    return LeetCodeClient()


def _get_luogu_client(sleep_sec: Optional[float] = None) -> LuoguClient:
    if sleep_sec is not None:
        return LuoguClient(sleep_sec=sleep_sec)
    return LuoguClient()

# 当运行到"/leetcode/profile_meta"，FastAPi会自动执行其下方的函数def
@app.post(
    "/leetcode/profile_meta",
    response_model=OkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)

def leetcode_profile_meta(req: UserRequest) -> OkResponse:
    client = _get_client(req.sleep_sec)
    meta = client.fetch_profile_meta(req.username)
    return OkResponse(data={"meta": meta})


@app.post(
    "/leetcode/recent_ac",
    response_model=OkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def leetcode_recent_ac(req: UserRequest) -> OkResponse:
    client = _get_client(req.sleep_sec)
    items = client.fetch_recent_ac(req.username)
    out = [
        {
            "title": it.title,
            "slug": it.slug,
            "timestamp": it.timestamp,
            "time": format_local_time(it.timestamp),
        }
        for it in items
    ]
    return OkResponse(data={"recent_accepted": out})


@app.post(
    "/leetcode/submit_stats",
    response_model=OkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def leetcode_submit_stats(req: UserRequest) -> OkResponse:
    client = _get_client(req.sleep_sec)
    stats = client.fetch_user_submit_stats(req.username)
    return OkResponse(data={"stats": stats})


@app.post(
    "/leetcode/public_profile",
    response_model=OkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def leetcode_public_profile(req: UserRequest) -> OkResponse:
    client = _get_client(req.sleep_sec)
    profile = client.fetch_user_public_profile(req.username)
    return OkResponse(data={"profile": profile})


@app.post(
    "/luogu/practice",
    response_model=OkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def luogu_practice(req: LuoguUserRequest) -> OkResponse:
    client = _get_luogu_client(req.sleep_sec)
    data = client.fetch_user_practice(req.uid)
    return OkResponse(data=data)


@app.post(
    "/leetcode/crawl",
    response_model=OkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def leetcode_crawl(req: UserRequest) -> OkResponse:
    client = _get_client(req.sleep_sec)
    meta = client.fetch_profile_meta(req.username)
    if not meta.get("exists"):
        return OkResponse(data={"meta": meta, "recent_accepted": [], "stats": None})

    ac_items = client.fetch_recent_ac(req.username)
    ac_out = [
        {
            "title": it.title,
            "slug": it.slug,
            "timestamp": it.timestamp,
            "time": format_local_time(it.timestamp),
        }
        for it in ac_items
    ]

    stats = client.fetch_user_submit_stats(req.username)
    return OkResponse(data={"meta": meta, "recent_accepted": ac_out, "stats": stats})