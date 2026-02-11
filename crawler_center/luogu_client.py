from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import requests
from lxml import html

from .config import settings


class LuoguClient:
    def __init__(
        self,
        timeout: int = settings.DEFAULT_TIMEOUT,
        sleep_sec: float = settings.DEFAULT_SLEEP_SEC,
        user_agent: Optional[str] = None,
    ):
        self.base_url = settings.LUOGU_BASE_URL.rstrip("/")
        self.timeout = timeout
        self.sleep_sec = sleep_sec
        self.sess = requests.Session()
        self.sess.headers.update(
            {
                "User-Agent": user_agent or settings.DEFAULT_USER_AGENT,
                "Accept": "text/html,application/json",
            }
        )

    def practice_url(self, uid: int) -> str:
        return f"{self.base_url}/user/{uid}/practice"

    def fetch_lentille_context(self, uid: int) -> Dict[str, Any]:
        """
        优先尝试：带 x-lentille-request: content-only 直接拿 JSON（更干净）
        如果服务端仍返回 HTML：退回到解析 HTML 里的 script#lentille-context
        """
        url = self.practice_url(uid)
        
        # 1) 尝试 content-only（如果站点支持会直接返回 JSON）
        time.sleep(self.sleep_sec)
        r = self.sess.get(
            url, 
            headers={"x-lentille-request": "content-only"}, 
            timeout=self.timeout
        )
        if r.status_code == 404:
            return {}
        r.raise_for_status()

        # 如果就是 JSON，直接 loads
        ct = (r.headers.get("Content-Type") or "").lower()
        if "application/json" in ct:
            return r.json()

        # 2) 否则按 HTML 解析 script#lentille-context
        doc = html.fromstring(r.text)
        node = doc.xpath("//script[@id='lentille-context']/text()")
        if not node or not node[0].strip():
            # 可能是权限问题或者页面结构变更，这里视为没取到
            return {}

        return json.loads(node[0])

    def fetch_user_practice(self, uid: int) -> Dict[str, Any]:
        ctx = self.fetch_lentille_context(uid)
        if not ctx:
            return {"user": None, "passed": [], "passed_count": 0}
            
        return self._extract_user_practice(ctx)

    def _extract_user_practice(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        ctx 的结构大致是：
        {
          "data": {
            "passed": [...],
            "submitted": [...],
            "user": {...目标用户...}
          }
        }
        """
        data = ctx.get("data") or {}
        user = data.get("user") or {}
        passed = data.get("passed") or []

        # 目标用户信息
        user_info = {
            "uid": user.get("uid"),
            "name": user.get("name") or "",
            "avatar": user.get("avatar") or "",
        }

        # 做过/通过题目列表（passed）
        passed_problems = []
        for it in passed:
            passed_problems.append({
                "pid": it.get("pid", ""),
                "title": it.get("title", ""),
                "difficulty": it.get("difficulty", None),
                "type": it.get("type", ""),
            })

        return {
            "user": user_info,
            "passed": passed_problems,
            "passed_count": len(passed_problems),
        }
