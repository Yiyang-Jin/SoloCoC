"""CoC 行动日志：记录对话、投骰、技能检定等。"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

Path(config.COC_SESSIONS_DIR).mkdir(parents=True, exist_ok=True)


def _log_path(session_id: str) -> Path:
    return Path(config.COC_SESSIONS_DIR) / f"{session_id}_log.json"


def append_log(session_id: str, entry: dict) -> None:
    """追加一条行动日志。"""
    p = _log_path(session_id)
    entries = []
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []
    entry.setdefault("time", datetime.now().isoformat())
    entries.append(entry)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=0)


def get_log(session_id: str) -> list[dict]:
    """获取指定会话的完整行动日志。"""
    p = _log_path(session_id)
    if not p.exists():
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
