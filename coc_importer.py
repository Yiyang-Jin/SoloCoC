"""人物卡导入器：支持 PDF、JSON、TXT、MD、HTML、DOCX 等格式。"""
import copy
import json
import re
from pathlib import Path
from typing import Optional

import coc_storage
import coc_qwen


def _extract_pdf_text(file_path: str | Path) -> str:
    """PDF 提取：优先 pdfplumber（表格更好），否则 pypdf。返回全部页拼接的文本。"""
    path = Path(file_path)
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
        return "\n\n".join(parts)
    except ImportError:
        pass
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return "\n\n".join(p.extract_text() or "" for p in reader.pages)


def _extract_pdf_pages(file_path: str | Path) -> list[str]:
    """PDF 按页提取，返回每页文本列表。用于多人物卡分块。"""
    path = Path(file_path)
    pages = []
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                pages.append(t.strip() if t else "")
    except ImportError:
        pass
    if not pages:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = [p.extract_text() or "" for p in reader.pages]
    return pages


def _extract_docx_text(file_path: str | Path) -> str:
    """DOCX 提取。"""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("需要安装 python-docx: pip install python-docx")
    doc = Document(str(file_path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_html_text(file_path: str | Path) -> str:
    """HTML 提取，去标签。"""
    from html.parser import HTMLParser
    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
        def handle_data(self, data):
            self.text.append(data)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    p = TextExtractor()
    p.feed(content)
    return re.sub(r"\s+", " ", " ".join(p.text)).strip()


def _extract_text(file_path: str | Path) -> str:
    """纯文本 / MD 提取。"""
    path = Path(file_path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _detect_ext_from_bytes(raw_bytes: bytes) -> str:
    """从 magic bytes 推测扩展名。"""
    if len(raw_bytes) >= 4 and raw_bytes[:4] == b"%PDF":
        return ".pdf"
    if len(raw_bytes) >= 2 and raw_bytes[:2] == b"PK":
        return ".docx"
    if len(raw_bytes) >= 5 and (raw_bytes[:5] == b"<!DO" or raw_bytes[:5] == b"<html"):
        return ".html"
    if len(raw_bytes) >= 2 and raw_bytes[:2] in (b"{\"", b"[{"):
        return ".json"
    return ".txt"


def _detect_and_extract(
    file_path: str | Path = None,
    raw_bytes: Optional[bytes] = None,
) -> tuple[str, str, Optional[list[str]]]:
    """
    根据扩展名/内容检测格式并提取文本。
    返回 (扩展名, 文本内容, pdf_pages 或 None)。
    """
    import tempfile
    path = file_path
    pdf_pages = None
    if raw_bytes is not None:
        ext = _detect_ext_from_bytes(raw_bytes)
        if file_path:
            ext = Path(file_path).suffix.lower() or ext
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(raw_bytes)
            path = tmp.name
        try:
            text = _extract_by_ext(ext, path)
            if ext == ".pdf":
                pdf_pages = _extract_pdf_pages(path)
            return ext, text, pdf_pages
        finally:
            try:
                Path(path).unlink(missing_ok=True)
            except Exception:
                pass
    ext = Path(file_path).suffix.lower()
    text = _extract_by_ext(ext, file_path)
    if ext == ".pdf":
        pdf_pages = _extract_pdf_pages(file_path)
    return ext, text, pdf_pages


def _extract_by_ext(ext: str, path) -> str:
    ext = (ext or "").lower()
    if ext == ".pdf":
        return _extract_pdf_text(path)
    if ext in (".docx", ".doc"):
        return _extract_docx_text(path)
    if ext in (".html", ".htm"):
        return _extract_html_text(path)
    if ext in (".txt", ".md", ".markdown", ""):
        return _extract_text(path)
    if ext == ".json":
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    return _extract_text(path)


def _split_into_character_chunks(
    text: str,
    source_ext: str,
    pdf_pages: Optional[list[str]] = None,
) -> list[str]:
    """
    将长文本切分为多个「可能是单个人物卡」的块。
    - JSON：可能是数组，直接解析
    - PDF：先按分隔符切，若只得到 1 块且有多页，则按页切分
    """
    text = text.strip()
    if not text:
        return []

    if source_ext == ".json":
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [json.dumps(x, ensure_ascii=False) for x in data if isinstance(x, dict)]
            if isinstance(data, dict):
                return [json.dumps(data, ensure_ascii=False)]
        except json.JSONDecodeError:
            pass

    if source_ext == ".pdf":
        age_occ_parts = re.split(r"\n(?=年龄:\s*\d+\s+职业:)", text)
        if len(age_occ_parts) > 1:
            chunks = []
            for i, p in enumerate(age_occ_parts):
                p = p.strip()
                if not p:
                    continue
                if i == 0 and "年龄:" not in p:
                    if len(p) < 60:
                        continue
                    if len(age_occ_parts) > 1 and age_occ_parts[1].strip():
                        p = p + "\n" + age_occ_parts[1].strip()
                        age_occ_parts[1] = ""
                if len(p) >= 150:
                    chunks.append(p)
            if chunks:
                return chunks
        name_age_parts = re.split(r"\n\n(?=[^\n]{2,25}\n\s*年龄:\s*\d+)", text)
        if len(name_age_parts) > 1:
            chunks = [p.strip() for p in name_age_parts if p.strip() and len(p.strip()) > 150]
            if chunks:
                return chunks

    separators = [
        r"\n-{3,}\n",
        r"\n={3,}\n",
        r"\n(?:第[一二三四五六七八九十\d]+[个位]? ?(?:调查员|人物卡|角色))\s*\n",
        r"\n(?:调查员|人物卡|角色)[\s\d]*[：:]\s*\n",
        r"\n(?:姓名|角色名|名字)[：:]\s*\n",
        r"\n【[^】]+】\s*\n",
    ]
    chunks = [text]
    for sep in separators:
        new_chunks = []
        for c in chunks:
            parts = re.split(sep, c, flags=re.IGNORECASE)
            new_chunks.extend(p for p in parts if p.strip() and len(p.strip()) > 50)
        if len(new_chunks) > len(chunks):
            chunks = new_chunks

    if len(chunks) == 1 and len(text) > 2000:
        sub = re.split(r"\n\s*\n(?=[^\n]*年龄:\s*\d+)", text)
        chunks = [s.strip() for s in sub if len(s.strip()) > 150]

    if source_ext == ".pdf" and len(chunks) == 1 and pdf_pages and len(pdf_pages) >= 2:
        chunks = [p for p in pdf_pages if p.strip() and len(p.strip()) > 200]

    return [c for c in chunks if c.strip()]


def _strip_pop_cthulhu_section(text: str) -> str:
    """剔除原文中的通俗克苏鲁/通俗调整区块，仅保留标准规则内容。"""
    for marker in ["通俗调整", "通俗克苏鲁", "英雄类型："]:
        if marker in text:
            text = text[: text.find(marker)].rstrip()
    return text


def _parse_chunk_to_character(chunk: str, use_llm: bool = True) -> Optional[dict]:
    """将单块文本解析为人物卡 dict。先尝试 JSON，否则用 LLM。"""
    chunk = _strip_pop_cthulhu_section(chunk.strip())
    if chunk.startswith("{"):
        try:
            data = json.loads(chunk)
            if isinstance(data, dict) and data.get("name") or data.get("attributes"):
                return _normalize_character(data)
        except json.JSONDecodeError:
            for m in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", chunk):
                try:
                    data = json.loads(m.group(0))
                    if isinstance(data, dict):
                        return _normalize_character(data)
                except json.JSONDecodeError:
                    continue

    if use_llm and len(chunk) > 50:
        return coc_qwen.parse_text_to_character(chunk)
    return None


def _normalize_character(data: dict) -> dict:
    """标准化为内部人物卡结构。剔除通俗克苏鲁相关字段。"""
    pop_keys = {"hero_type", "heroType", "talents", "天赋", "通俗调整", "通俗克苏鲁", "pop_skill_adjust", "pop_attrs"}
    for k in list(data.keys()):
        if any(p in str(k) for p in ("通俗", "英雄", "天赋")):
            data.pop(k, None)
    for k in pop_keys:
        data.pop(k, None)
    out = copy.deepcopy(coc_storage.COC_CHAR_TEMPLATE)
    attrs = data.get("attributes") or {}
    if isinstance(attrs, dict):
        for k in out["attributes"]:
            if k in attrs and attrs[k] is not None:
                v = attrs[k]
                out["attributes"][k] = int(v) if isinstance(v, (int, float)) and k != "Luck" else v
    for key in ["name", "age", "occupation", "nationality", "background", "appearance", "traits", "beliefs", "treasure"]:
        if key in data and data[key] is not None:
            out[key] = data[key]
    out["skills"] = data.get("skills") or []
    out["combat"] = data.get("combat") or []
    return out


def import_from_file(
    file_path: str | Path = None,
    raw_bytes: Optional[bytes] = None,
    use_llm: bool = True,
) -> list[dict]:
    """
    从文件导入人物卡。支持 PDF/JSON/TXT/MD/HTML/DOCX。
    PDF 支持从单文件中读取多个人物卡（按分隔符或按页切分）。
    返回成功导入的人物卡列表 [{character_id, name, ...}, ...]。
    """
    ext, text, pdf_pages = _detect_and_extract(file_path, raw_bytes)
    chunks = _split_into_character_chunks(text, ext, pdf_pages=pdf_pages)
    if not chunks:
        chunks = [text] if text.strip() else []

    saved = []
    for chunk in chunks:
        char = _parse_chunk_to_character(chunk, use_llm=use_llm)
        if char:
            cid = coc_storage.save_character(None, char)
            saved.append({"character_id": cid, "name": char.get("name", "未命名"), **char})
    return saved
