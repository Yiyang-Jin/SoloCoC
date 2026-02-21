"""FastAPI 主入口 - CoC 跑团助手。"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
import uuid
from pathlib import Path

import settings_store
import api_config
import config
import coc_dice
import coc_storage
import coc_qwen
import coc_rag
import coc_map
import coc_log
import coc_importer
import coc_constants

app = FastAPI(title="CoC 跑团助手")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ----- 请求体 -----
class RollDiceReq(BaseModel):
    expr: str
    session_id: Optional[str] = None


class GenerateCharacterReq(BaseModel):
    occupation: str = ""
    nationality: str = ""
    extra_hint: str = ""


class KpChatReq(BaseModel):
    session_id: str
    script_id: str
    message: str
    character_id: Optional[str] = None
    is_character_action: bool = False


class SaveCharacterReq(BaseModel):
    id: Optional[str] = None
    data: dict


class InferActionReq(BaseModel):
    character_id: str
    session_id: str
    script_id: Optional[str] = None


class GeneratePersonaReq(BaseModel):
    name: str = ""
    age: int = 0
    occupation: str = ""
    nationality: str = ""
    extra_hint: str = ""


class SuggestSkillsReq(BaseModel):
    occupation: str
    edu: int = 65
    int_val: int = 65


class SetKpPromptReq(BaseModel):
    prompt: str


class UpdateSettingsReq(BaseModel):
    temperature: Optional[float] = None
    top_p: Optional[float] = None


class SetApiKeyReq(BaseModel):
    api_key: str


class SetConfigReq(BaseModel):
    provider: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None


# ----- 路由 -----
@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.post("/api/coc/characters/infer-action")
def coc_infer_action_api(req: InferActionReq):
    character = coc_storage.get_character(req.character_id)
    if not character:
        raise HTTPException(404, "人物卡不存在")
    history_path = Path(config.COC_SESSIONS_DIR) / f"{req.session_id}.json"
    history = []
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
    script_context = ""
    if req.script_id:
        last_user = next((h.get("content", "") for h in reversed(history) if h.get("role") == "user"), "")
        last_kp = next((h.get("content", "") for h in reversed(history) if h.get("role") == "assistant"), "")
        query = last_kp[:200] if last_kp else last_user[:200] or "调查 场景"
        script_context = coc_rag.retrieve(req.script_id, query)
    gen = settings_store.get_settings()
    action = coc_qwen.infer_character_action(
        character_card=character,
        chat_history=history,
        script_context=script_context,
        temperature=gen.get("temperature", 0.85),
        top_p=gen.get("top_p", 0.9),
    )
    return {"action": action}


@app.get("/api/coc/characters")
def coc_list_characters():
    return coc_storage.list_characters()


@app.get("/api/coc/characters/{char_id}")
def coc_get_character(char_id: str):
    c = coc_storage.get_character(char_id)
    if not c:
        raise HTTPException(404, "人物卡不存在")
    return c


@app.post("/api/coc/characters")
def coc_save_character_api(req: SaveCharacterReq):
    cid = coc_storage.save_character(req.id, req.data)
    return {"character_id": cid, "message": "ok"}


@app.delete("/api/coc/characters/{char_id}")
def coc_delete_character_api(char_id: str):
    coc_storage.delete_character(char_id)
    return {"message": "ok"}


@app.get("/api/coc/constants")
def coc_get_constants():
    return {"skills": coc_constants.COC_SKILLS, "occupations": coc_constants.COC_OCCUPATIONS}


@app.post("/api/coc/characters/persona")
def coc_generate_persona_api(req: GeneratePersonaReq):
    gen = settings_store.get_settings()
    data = coc_qwen.generate_persona(
        name=req.name,
        age=req.age,
        occupation=req.occupation,
        nationality=req.nationality,
        extra_hint=req.extra_hint,
        temperature=gen.get("temperature", 0.85),
        top_p=gen.get("top_p", 0.9),
    )
    return data


@app.post("/api/coc/characters/suggest-skills")
def coc_suggest_skills_api(req: SuggestSkillsReq):
    gen = settings_store.get_settings()
    skills = coc_qwen.suggest_skills_for_occupation(
        occupation=req.occupation,
        edu=req.edu,
        int_val=req.int_val,
        temperature=gen.get("temperature", 0.3),
        top_p=gen.get("top_p", 0.9),
    )
    return {"skills": skills}


@app.post("/api/coc/characters/import")
async def coc_import_characters_api(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "请选择文件")
    ext = Path(file.filename).suffix.lower()
    allowed = {".pdf", ".json", ".txt", ".md", ".html", ".htm", ".docx", ".doc"}
    if ext not in allowed:
        raise HTTPException(400, f"不支持的文件类型 {ext}，支持: PDF, JSON, TXT, MD, HTML, DOCX")
    content = await file.read()
    try:
        saved = coc_importer.import_from_file(file_path=file.filename, raw_bytes=content)
    except Exception as e:
        raise HTTPException(400, f"导入失败: {e}") from e
    return {"imported": len(saved), "characters": saved}


@app.post("/api/coc/characters/generate")
def coc_generate_character_api(req: GenerateCharacterReq):
    gen = settings_store.get_settings()
    data = coc_qwen.generate_character_card(
        occupation=req.occupation,
        nationality=req.nationality,
        extra_hint=req.extra_hint,
        temperature=gen.get("temperature", 0.9),
        top_p=gen.get("top_p", 0.9),
    )
    cid = coc_storage.save_character(None, data)
    return {"character_id": cid, "character": data}


@app.post("/api/coc/dice/roll-attributes")
def coc_roll_attributes_api():
    rolls = []
    for i in range(8):
        if i in (2, 4):
            v, desc = coc_dice.roll("2d6")
            v = v + 6
            rolls.append((v, f"2D6+6={desc}+6"))
        else:
            v, desc = coc_dice.roll("3d6")
            rolls.append((v, desc))
    STR, CON, SIZ, DEX, INT, APP, POW, EDU = [r[0] for r in rolls]
    SIZ = max(SIZ, 6)
    EDU = max(EDU, 6)
    SAN = POW * 5
    HP = (CON + SIZ) // 10
    MP = POW // 5
    total = STR + SIZ
    if total <= 64:
        DB, Build = -2, -2
    elif total <= 84:
        DB, Build = -1, -1
    elif total <= 124:
        DB, Build = 0, 0
    elif total <= 164:
        DB, Build = 1, 1
    else:
        DB, Build = 2, 2
    MOVE = 8 if DEX >= SIZ else 7
    luck_r, luck_d = coc_dice.roll("3d6")
    Luck = luck_r * 5
    return {
        "attributes": {"STR": STR, "CON": CON, "SIZ": SIZ, "DEX": DEX, "INT": INT, "APP": APP, "POW": POW, "EDU": EDU},
        "derived": {"SAN": SAN, "HP": HP, "MP": MP, "DB": DB, "Build": Build, "MOVE": MOVE, "Luck": Luck},
        "roll_descs": {k: v[1] for k, v in zip(["STR", "CON", "SIZ", "DEX", "INT", "APP", "POW", "EDU"], rolls)},
    }


@app.post("/api/coc/dice/roll")
def coc_roll_dice_api(req: RollDiceReq):
    try:
        total, desc = coc_dice.roll(req.expr)
        if req.session_id:
            coc_log.append_log(req.session_id, {
                "type": "dice",
                "expr": req.expr,
                "result": total,
                "description": desc,
            })
        return {"result": total, "description": desc}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/coc/dice/skill-check")
def coc_skill_check_api(skill_value: int, session_id: Optional[str] = None):
    success, roll_val, desc = coc_dice.roll_skill_check(skill_value)
    if session_id:
        coc_log.append_log(session_id, {
            "type": "skill_check",
            "skill_value": skill_value,
            "roll": roll_val,
            "success": success,
            "description": desc,
        })
    return {"success": success, "roll": roll_val, "description": desc}


@app.get("/api/coc/scripts")
def coc_list_scripts():
    return coc_rag.list_scripts()


@app.get("/api/coc/maps")
def coc_list_maps():
    return coc_map.list_maps()


def _map_media_type(path: Path) -> str:
    ext = str(path).lower().split(".")[-1] if "." in str(path) else ""
    if ext in ("png",): return "image/png"
    if ext in ("jpg", "jpeg",): return "image/jpeg"
    if ext in ("webp",): return "image/webp"
    return "application/octet-stream"


@app.get("/api/coc/maps/{map_id}/image")
def coc_get_map_image(map_id: str):
    p = coc_map.get_map_image_path(map_id)
    if not p or not p.exists():
        raise HTTPException(404, "地图不存在")
    return FileResponse(str(p), media_type=_map_media_type(p))


@app.post("/api/coc/maps/upload")
async def coc_upload_map(file: UploadFile = File(...), map_id: str = Form(None)):
    if not file.filename:
        raise HTTPException(400, "请选择文件")
    ext = Path(file.filename).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
        raise HTTPException(400, "仅支持 PNG/JPG/JPEG/WEBP/BMP 图片")
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        ok, msg, mid = coc_map.process_map_upload(tmp_path, map_id)
        if not ok:
            raise HTTPException(400, msg)
        return {"map_id": mid, "message": msg}
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.delete("/api/coc/maps/{map_id}")
def coc_delete_map_api(map_id: str):
    if not coc_map.delete_map(map_id):
        raise HTTPException(404, "地图不存在")
    return {"message": "ok"}


@app.get("/api/coc/kp-prompt")
def coc_get_kp_prompt():
    return {"prompt": coc_qwen._load_kp_prompt()}


@app.put("/api/coc/kp-prompt")
def coc_set_kp_prompt(req: SetKpPromptReq):
    p = Path(config.COC_DATA_DIR) / "kp_prompt.txt"
    Path(config.COC_DATA_DIR).mkdir(parents=True, exist_ok=True)
    p.write_text(req.prompt.strip(), encoding="utf-8")
    return {"message": "ok"}


@app.delete("/api/coc/kp-prompt")
def coc_reset_kp_prompt():
    p = Path(config.COC_DATA_DIR) / "kp_prompt.txt"
    if p.exists():
        p.unlink()
    return {"message": "ok", "prompt": coc_qwen._load_kp_prompt()}


@app.get("/api/coc/sessions/{session_id}/log")
def coc_get_action_log(session_id: str):
    return coc_log.get_log(session_id)


@app.post("/api/coc/scripts/upload")
async def coc_upload_script(
    file: UploadFile = File(...),
    script_id: str = Form(None),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "请上传 PDF 文件")
    sid = (script_id or "").strip() or str(uuid.uuid4())[:8]
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        ok, msg = coc_rag.process_pdf_upload(tmp_path, sid)
        if not ok:
            raise HTTPException(400, msg)
        return {"script_id": sid, "message": msg}
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.post("/api/coc/kp/chat")
def coc_kp_chat_api(req: KpChatReq):
    if not req.script_id:
        raise HTTPException(400, "请先上传剧本")
    script_context = coc_rag.retrieve(req.script_id, req.message)
    map_list = coc_map.get_all_maps_for_prompt()
    context_for_map = (req.message or "") + "\n" + (script_context or "")
    map_image_path = coc_map.get_image_path_for_context(context_for_map)
    character = coc_storage.get_character(req.character_id) if req.character_id else None
    history_path = Path(config.COC_SESSIONS_DIR) / f"{req.session_id}.json"
    history = []
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
    gen = settings_store.get_settings()
    reply = coc_qwen.kp_chat(
        script_context=script_context,
        map_list=map_list,
        map_image_path=map_image_path,
        chat_history=history,
        user_message=req.message,
        character_card=character,
        is_character_action=req.is_character_action,
        session_id=req.session_id,
        temperature=gen.get("temperature", 0.85),
        top_p=gen.get("top_p", 0.9),
    )
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    history = history[-50:]
    Path(config.COC_SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=0)
    char_name = (character or {}).get("name", "")
    coc_log.append_log(req.session_id, {
        "type": "chat_user",
        "content": req.message,
        "character_id": req.character_id,
        "character_name": char_name,
        "is_character_action": req.is_character_action,
    })
    coc_log.append_log(req.session_id, {"type": "chat_kp", "content": reply})
    return {"reply": reply}


@app.get("/api/settings")
def get_settings_api():
    return settings_store.get_settings()


@app.get("/api/config")
def get_config_api():
    """返回完整配置（含 providers 列表，不返回 API Key 原文）。"""
    return api_config.get_full_config()


@app.put("/api/config")
def update_config_api(req: SetConfigReq):
    """保存 LLM 配置（provider、base_url、model、api_key）。"""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if updates:
        api_config.set_config(**updates)
    return {"message": "ok", **api_config.get_full_config()}


@app.put("/api/settings")
def update_settings_api(req: UpdateSettingsReq):
    d = {k: v for k, v in req.model_dump().items() if v is not None}
    return settings_store.save_settings(d)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=29147)
