from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class Settings:
    # LeetCode 配置
    LEETCODE_BASE_URL: str
    
    # Luogu 配置
    LUOGU_BASE_URL: str
    
    # 爬虫默认行为配置
    DEFAULT_TIMEOUT: int
    DEFAULT_SLEEP_SEC: float
    
    # 伪装配置
    DEFAULT_USER_AGENT: str

    # API 服务配置
    API_TITLE: str
    API_VERSION: str

    @classmethod
    def load_from_yaml(cls, path: str = "config.yaml") -> Settings:
        # 寻找 config.yaml 路径
        # 优先查找当前工作目录，其次查找项目根目录（假设当前文件在 crawler_center/config.py）
        yaml_path = Path(path)
        if not yaml_path.exists():
            # 尝试向上找一级 (项目根目录)
            root_yaml = Path(__file__).parent.parent / path
            if root_yaml.exists():
                yaml_path = root_yaml
        
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}

        # 提取各部分配置，提供默认兜底（以防 YAML 缺字段）
        leetcode_conf = data.get("leetcode", {})
        luogu_conf = data.get("luogu", {})
        crawler_conf = data.get("crawler", {})
        api_conf = data.get("api", {})

        return cls(
            LEETCODE_BASE_URL=leetcode_conf.get("base_url", "https://leetcode.cn"),
            LUOGU_BASE_URL=luogu_conf.get("base_url", "https://www.luogu.com.cn"),
            
            DEFAULT_TIMEOUT=int(crawler_conf.get("default_timeout", 15)),
            DEFAULT_SLEEP_SEC=float(crawler_conf.get("default_sleep_sec", 0.8)),
            DEFAULT_USER_AGENT=crawler_conf.get("default_user_agent", ""),
            
            API_TITLE=api_conf.get("title", "crawler_center"),
            API_VERSION=api_conf.get("version", "0.1.0"),
        )


# 单例加载
try:
    settings = Settings.load_from_yaml()
except Exception as e:
    print(f"Warning: Failed to load config.yaml, using defaults. Error: {e}")
    # 兜底默认值
    settings = Settings(
        LEETCODE_BASE_URL="https://leetcode.cn",
        LUOGU_BASE_URL="https://www.luogu.com.cn",
        DEFAULT_TIMEOUT=15,
        DEFAULT_SLEEP_SEC=0.8,
        DEFAULT_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        API_TITLE="crawler_center",
        API_VERSION="0.1.0"
    )
