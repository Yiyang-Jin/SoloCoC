"""剧本 PDF 解析与 RAG 检索（BM25）。"""
import json
import os
from pathlib import Path
from typing import Optional

import config
import jieba
from pypdf import PdfReader
from rank_bm25 import BM25Okapi

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
TOP_K = 5

_script_index: dict[str, tuple[list[str], BM25Okapi]] = {}


def _ensure_scripts_dir() -> Path:
    Path(config.COC_SCRIPTS_DIR).mkdir(parents=True, exist_ok=True)
    return Path(config.COC_SCRIPTS_DIR)


def extract_text_from_pdf(file_path: str | Path) -> str:
    """从 PDF 提取文本。"""
    reader = PdfReader(str(file_path))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _tokenize(text: str) -> list[str]:
    """中文分词，用于 BM25。"""
    return list(jieba.cut_for_search(text))


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """按固定长度分块，带重叠。"""
    if len(text) <= size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


def index_script(script_id: str, text: str) -> None:
    """对剧本文本建 BM25 索引。"""
    chunks = chunk_text(text)
    if not chunks:
        _script_index[script_id] = ([], BM25Okapi([[]]))
        return
    tokenized = [_tokenize(c) for c in chunks]
    bm25 = BM25Okapi(tokenized)
    _script_index[script_id] = (chunks, bm25)


def load_script_index(script_id: str) -> bool:
    """从文件加载已建索引。"""
    base = _ensure_scripts_dir()
    meta_path = base / script_id / "meta.json"
    chunks_path = base / script_id / "chunks.json"
    if not meta_path.exists() or not chunks_path.exists():
        return False
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        if not chunks:
            _script_index[script_id] = ([], BM25Okapi([[]]))
            return True
        tokenized = [_tokenize(c) for c in chunks]
        bm25 = BM25Okapi(tokenized)
        _script_index[script_id] = (chunks, bm25)
        return True
    except Exception:
        return False


def save_script_index(script_id: str, chunks: list[str]) -> None:
    """保存分块到文件，便于下次加载。"""
    base = _ensure_scripts_dir()
    script_dir = base / script_id
    script_dir.mkdir(parents=True, exist_ok=True)
    with open(script_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=0)


def retrieve(script_id: str, query: str, top_k: int = TOP_K) -> str:
    """
    根据查询检索相关剧本片段。
    返回拼接后的上下文字符串。
    """
    if script_id not in _script_index:
        if not load_script_index(script_id):
            return ""
    chunks, bm25 = _script_index.get(script_id, ([], None))
    if not chunks or bm25 is None:
        return ""
    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    selected = [chunks[i] for i in indices if scores[i] > 0]
    if not selected:
        selected = chunks[:2]  #  fallback
    return "\n\n---\n\n".join(selected)


def process_pdf_upload(file_path: str | Path, script_id: str) -> tuple[bool, str]:
    """
    处理上传的 PDF 剧本。
    提取文本 → 分块 → 建索引 → 保存。
    返回 (成功, 消息)。
    """
    try:
        text = extract_text_from_pdf(file_path)
    except Exception as e:
        return False, f"PDF 解析失败: {e}"

    if not text.strip():
        return False, "PDF 中未提取到有效文本"

    chunks = chunk_text(text)
    if not chunks:
        return False, "分块后为空"

    index_script(script_id, text)
    save_script_index(script_id, chunks)

    base = _ensure_scripts_dir()
    script_dir = base / script_id
    script_dir.mkdir(parents=True, exist_ok=True)
    with open(script_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "script_id": script_id,
            "total_chars": len(text),
            "chunk_count": len(chunks),
        }, f, ensure_ascii=False, indent=2)

    return True, f"已索引 {len(text)} 字，{len(chunks)} 个分块"


def list_scripts() -> list[dict]:
    """列出已上传的剧本。"""
    base = _ensure_scripts_dir()
    out = []
    for d in base.iterdir():
        if d.is_dir():
            meta_path = d / "meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    out.append({"id": d.name, **meta})
                except Exception:
                    pass
    return out
