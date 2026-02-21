"""地图模块：上传地图图片，按文件名管理。每次对话注入全部地图名，由 LLM 判断适用性；按文件名匹配决定是否传入图像。"""
import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Optional

import config

_cached_maps: list[dict] | None = None


def _ensure_maps_dir() -> Path:
    Path(config.COC_MAPS_DIR).mkdir(parents=True, exist_ok=True)
    return Path(config.COC_MAPS_DIR)


def _load_maps() -> list[dict]:
    """从磁盘加载所有地图元数据（map_id, filename, file_path）。"""
    global _cached_maps
    if _cached_maps is not None:
        return _cached_maps
    base = _ensure_maps_dir()
    out = []
    for d in base.iterdir():
        if not d.is_dir():
            continue
        meta_path = d / "meta.json"
        if not meta_path.exists():
            continue
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            mid = meta.get("map_id", d.name)
            img_name = meta.get("image_filename", meta.get("filename", ""))
            img_path = d / img_name if img_name and (d / img_name).exists() else None
            out.append({
                "map_id": mid,
                "filename": meta.get("filename", img_name or ""),
                "file_path": str(img_path) if img_path else None,
            })
        except Exception:
            pass
    _cached_maps = out
    return out


def get_all_maps_for_prompt() -> list[dict]:
    """
    返回全部地图列表，供每次对话注入 prompt。
    返回 [{"map_id", "filename", "file_path"}, ...]
    """
    return _load_maps()


def get_image_path_for_context(context: str) -> Optional[str]:
    """
    根据当前语境（用户输入 + 剧本片段）判断是否应传入某张地图图像。
    规则：若某地图文件名（去除扩展名）中的有意义部分出现在 context 中，则返回该地图的 file_path。
    用于规范命名的地图（如「奈亚拉托提普的面具」33 张图），减少剧本仅提及地点就误传图的问题。
    """
    if not context or not context.strip():
        return None
    ctx_lower = context.strip().lower()
    maps_list = _load_maps()
    for m in maps_list:
        fp = m.get("file_path")
        if not fp:
            continue
        fn = m.get("filename", "")
        stem = Path(fn).stem
        # 提取文件名中的有意义片段：中文、英文等，至少 2 字符
        words = re.findall(r"[\u4e00-\u9fff\u3000-\u303f\w]{2,}", stem)
        for w in words:
            if len(w) >= 2 and w.lower() in ctx_lower:
                return fp
    return None


def process_map_upload(file_path: str | Path, map_id: Optional[str] = None) -> tuple[bool, str, Optional[str]]:
    """
    处理上传的地图图片。仅保存文件，不进行 OCR。
    返回 (成功, 消息, map_id)。
    """
    global _cached_maps
    _cached_maps = None
    path = Path(file_path)
    if not path.exists():
        return False, "文件不存在", None
    ext = path.suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
        return False, f"不支持格式 {ext}，支持 PNG/JPG/JPEG/WEBP/BMP", None

    mid = (map_id or "").strip() or str(uuid.uuid4())[:12]
    base = _ensure_maps_dir()
    map_dir = base / mid
    map_dir.mkdir(parents=True, exist_ok=True)
    dest_name = path.name
    dest_path = map_dir / dest_name
    shutil.copy2(path, dest_path)

    meta = {
        "map_id": mid,
        "filename": path.name,
        "image_filename": dest_name,
    }
    with open(map_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return True, f"已上传 {dest_name}", mid


def list_maps() -> list[dict]:
    """列出已上传的地图。"""
    return _load_maps()


def delete_map(map_id: str) -> bool:
    """删除地图。"""
    global _cached_maps
    _cached_maps = None
    base = _ensure_maps_dir()
    map_dir = base / map_id
    if not map_dir.exists() or not map_dir.is_dir():
        return False
    try:
        shutil.rmtree(map_dir)
        return True
    except Exception:
        return False


def get_map_image_path(map_id: str) -> Optional[Path]:
    """获取地图图片的本地路径，用于前端展示或传给多模态模型。"""
    base = _ensure_maps_dir()
    map_dir = base / map_id
    meta_path = map_dir / "meta.json"
    if not meta_path.exists():
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        img_name = meta.get("image_filename", meta.get("filename", ""))
        if img_name:
            p = map_dir / img_name
            if p.exists():
                return p
    except Exception:
        pass
    return None
