from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import requests
from lxml import html

from .config import settings
from .leetcode_types import ACSubmission


class LeetCodeClient:
    def __init__(
        self,
        timeout: int = settings.DEFAULT_TIMEOUT,
        sleep_sec: float = settings.DEFAULT_SLEEP_SEC,
        user_agent: Optional[str] = None,
    ):
        self.base_url = settings.LEETCODE_BASE_URL
        self.timeout = timeout
        self.sleep_sec = sleep_sec
        self.sess = requests.Session()
        self.sess.headers.update(
            {
                "User-Agent": user_agent or settings.DEFAULT_USER_AGENT,
                "Accept": "text/html,application/json",
                "Content-Type": "application/json",
                "Origin": self.base_url,
            }
        )

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def profile_url(self, username: str) -> str:
        return self._build_url(f"u/{username}/")

    def graphql_url_recent_ac(self) -> str:
        return self._build_url("graphql/noj-go/")

    def graphql_url_user_stats(self) -> str:
        return self._build_url("graphql")

    def ensure_csrf(self) -> Optional[str]:
        token = self.sess.cookies.get("csrftoken")
        if token:
            return token
        try:
            self.sess.get(self._build_url(""), timeout=self.timeout)
        except Exception:
            return None
        return self.sess.cookies.get("csrftoken")

    def fetch_profile_meta(self, username: str) -> Dict[str, Any]:
        time.sleep(self.sleep_sec)
        url = self.profile_url(username)
        r = self.sess.get(url, allow_redirects=True, timeout=self.timeout)

        exists = r.status_code < 400 and r.status_code != 404
        if not exists:
            return {"exists": False, "reason": f"HTTP {r.status_code}", "url_final": r.url}

        doc = html.fromstring(r.text)
        og_title = doc.xpath("//meta[@property='og:title']/@content")
        og_desc = doc.xpath("//meta[@property='og:description']/@content")
        return {
            "exists": True,
            "url_final": r.url,
            "og_title": og_title[0] if og_title else "",
            "og_description": og_desc[0] if og_desc else "",
        }

    def _post_graphql(
        self,
        url: str,
        referer: str,
        payload: Dict[str, Any],
        csrf: Optional[str],
    ) -> Dict[str, Any]:
        headers: Dict[str, str] = {"Referer": referer}
        if csrf:
            headers["x-csrftoken"] = csrf
        time.sleep(self.sleep_sec)

        r = self.sess.post(url, json=payload, timeout=self.timeout, headers=headers)
        if r.status_code >= 400:
            snippet = (r.text or "").replace("\r", " ").replace("\n", " ")[:800]
            raise RuntimeError(f"GraphQL HTTP {r.status_code}: {snippet}")

        data = r.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {json.dumps(data['errors'], ensure_ascii=False)}")
        return data.get("data", {}) or {}

    def fetch_recent_ac(self, username: str) -> List[ACSubmission]:
        csrf = self.ensure_csrf()
        referer = self.profile_url(username)

        query = """
        query recentACSubmissions($userSlug: String!) {
          recentACSubmissions(userSlug: $userSlug) {
            submitTime
            question {
              title
              translatedTitle
              titleSlug
              questionFrontendId
            }
          }
        }
        """
        payload = {
            "operationName": "recentACSubmissions",
            "query": query.strip(),
            "variables": {"userSlug": username},
        }
        data = self._post_graphql(self.graphql_url_recent_ac(), referer, payload, csrf)
        items = data.get("recentACSubmissions", []) or []

        out: List[ACSubmission] = []
        for it in items:
            q = it.get("question") or {}
            title = q.get("translatedTitle") or q.get("title") or ""
            slug = q.get("titleSlug") or ""
            ts = int(it.get("submitTime") or 0)
            if title and slug and ts:
                out.append(ACSubmission(title=title, slug=slug, timestamp=ts))
        return out

    def fetch_user_submit_stats(self, username: str) -> Dict[str, Any]:
        csrf = self.ensure_csrf()
        referer = self.profile_url(username)
        query = """
        query userQuestionProgress($userSlug: String!) {
          userProfileUserQuestionSubmitStats(userSlug: $userSlug) {
            acSubmissionNum { difficulty count }
            totalSubmissionNum { difficulty count }
          }
          userProfileUserQuestionProgress(userSlug: $userSlug) {
            numAcceptedQuestions { difficulty count }
            numFailedQuestions { difficulty count }
            numUntouchedQuestions { difficulty count }
          }
        }
        """
        payload = {
            "operationName": "userQuestionProgress",
            "query": query.strip(),
            "variables": {"userSlug": username},
        }
        return self._post_graphql(self.graphql_url_user_stats(), referer, payload, csrf)

    def fetch_user_public_profile(self, username: str) -> Dict[str, str]:
        csrf = self.ensure_csrf()
        referer = self.profile_url(username)
        query = """
        query userPublicProfile($userSlug: String!) {
          userProfilePublicProfile(userSlug: $userSlug) {
            profile {
              userSlug
              realName
              userAvatar
            }
          }
        }
        """
        payload = {
            "operationName": "userPublicProfile",
            "query": query.strip(),
            "variables": {"userSlug": username},
        }
        data = self._post_graphql(self.graphql_url_user_stats(), referer, payload, csrf)
        root = data.get("userProfilePublicProfile") or {}
        profile = root.get("profile") or {}
        return {
            "userSlug": profile.get("userSlug") or "",
            "realName": profile.get("realName") or "",
            "userAvatar": profile.get("userAvatar") or "",
        }
