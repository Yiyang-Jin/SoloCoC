"""CoC 人物卡储存器。"""
import json
import os
import uuid
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

import config

Path(config.COC_CHARACTERS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.COC_SCRIPTS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.COC_SESSIONS_DIR).mkdir(parents=True, exist_ok=True)


def _character_path(char_id: str) -> Path:
    return Path(config.COC_CHARACTERS_DIR) / f"{char_id}.json"


def list_characters() -> list[dict]:
    """列出所有人物卡。"""
    base = Path(config.COC_CHARACTERS_DIR)
    if not base.exists():
        return []
    out = []
    for f in base.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            out.append({"id": f.stem, "name": data.get("name", "未命名"), **data})
        except Exception:
            pass
    return sorted(out, key=lambda x: (x.get("updated_at") or x.get("created_at") or ""), reverse=True)


def get_character(char_id: str) -> Optional[dict]:
    """获取单个人物卡。"""
    p = _character_path(char_id)
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_character(char_id: Optional[str], data: dict) -> str:
    """保存人物卡，返回 char_id。"""
    if not char_id:
        char_id = str(uuid.uuid4())[:8]
    data["id"] = char_id
    data["updated_at"] = datetime.now().isoformat()
    if "created_at" not in data:
        data["created_at"] = data["updated_at"]
    p = _character_path(char_id)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return char_id


def delete_character(char_id: str) -> bool:
    """删除人物卡。"""
    p = _character_path(char_id)
    if p.exists():
        p.unlink()
        return True
    return False


# CoC 人物卡标准结构（参考图片格式，不含肖像与通俗改编）
COC_CHAR_TEMPLATE = {
    "name": "",
    "age": 0,
    "occupation": "",
    "nationality": "",
    "attributes": {
        "STR": 0,
        "CON": 0,
        "SIZ": 0,
        "DEX": 0,
        "INT": 0,
        "APP": 0,
        "POW": 0,
        "EDU": 0,
        "SAN": 0,
        "HP": 0,
        "DB": 0,
        "Build": 0,
        "MOVE": 0,
        "MP": 0,
        "Luck": "投3D6×5",
    },
    "skills": [],
    "combat": [],
    "background": "",
    "appearance": "",
    "traits": "",
    "beliefs": "",
    "treasure": "",
}
