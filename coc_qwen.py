"""CoC 模块专用 LLM 调用：人物卡生成、KP 扮演。统一使用 OpenAI 兼容 API。"""
import json
import re
from pathlib import Path
from typing import Optional

from openai import OpenAI, APIError

import api_config
import config
import coc_dice


def _openai_client() -> OpenAI:
    base_url = api_config.get_base_url()
    if not base_url:
        raise ValueError("Please set LLM provider in Settings / 请在设置中选择 LLM 提供商")
    api_key = api_config.get_api_key()
    if not api_key and api_config.get_provider() not in ("ollama", "lmstudio", "custom"):
        raise ValueError("Please set API Key in Settings / 请在设置中配置 API Key")
    key = api_key or "ollama"
    return OpenAI(api_key=key, base_url=base_url)


def _api_error(e: Exception) -> str:
    resp = getattr(e, "response", None) if isinstance(e, APIError) else None
    if not resp:
        return str(e)
    try:
        text = getattr(resp, "text", None)
        if text is None and hasattr(resp, "read"):
            text = resp.read() or b""
        if not text:
            text = b""
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
    except Exception:
        text = ""
    if isinstance(text, str) and text.strip().startswith("{"):
        import json as _json
        try:
            body = _json.loads(text)
            err = body.get("error") or body
            return (err.get("message") if isinstance(err, dict) else str(err)) or str(e)
        except Exception:
            pass
    return str(e)[:300]


def _call(
    messages: list[dict],
    max_tokens: int = 8000,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> str:
    client = _openai_client()
    model = api_config.get_model()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
    except Exception as e:
        raise RuntimeError("API 错误: " + _api_error(e)) from e
    if not resp.choices:
        raise RuntimeError("API 返回空")
    return (resp.choices[0].message.content or "").strip()


def generate_persona(
    name: str = "",
    age: int = 0,
    occupation: str = "",
    nationality: str = "",
    extra_hint: str = "",
    temperature: float = 0.85,
    top_p: float = 0.9,
) -> dict:
    """AI 辅助生成人设：背景、形象、特质、信念、宝贵之物。仅人设，不涉及数值。"""
    system = """你是克苏鲁的呼唤（CoC）跑团专家。根据角色的姓名、年龄、职业、国籍等，生成人设文本。
仅输出 JSON：{"background":"背景故事","appearance":"形象描述","traits":"特质","beliefs":"思想与信念","treasure":"宝贵之物"}
- background：多段背景故事，有代入感
- appearance：外貌描述
- traits：性格特质
- beliefs：核心信念
- treasure：宝贵之物
仅输出 JSON，不要其它内容。使用标准 CoC 规则，不含通俗克苏鲁。"""
    user = f"姓名：{name or '未定'}\n年龄：{age}\n职业：{occupation or '调查员'}\n国籍：{nationality or '美国'}\n{f'额外要求：{extra_hint}' if extra_hint else ''}\n\n请生成人设 JSON。"
    raw = _call([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=temperature, top_p=top_p)
    text = raw.strip()
    for p in ("```json", "```"):
        if text.startswith(p):
            text = text[len(p):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"background": "", "appearance": "", "traits": "", "beliefs": "", "treasure": ""}


def suggest_skills_for_occupation(
    occupation: str,
    edu: int = 65,
    int_val: int = 65,
    temperature: float = 0.3,
    top_p: float = 0.9,
) -> list[dict]:
    """AI 辅助：根据职业建议技能分配。职业技能点 EDU×20，兴趣技能点 INT×10。"""
    occ_pts = edu * 20
    int_pts = int_val * 10
    system = """你是 CoC 第七版规则专家。根据职业，输出该职业的技能建议。

输出要求：严格 JSON 数组 [{"name":"技能名","value":数字,"type":"occupation|interest"}]
- type=occupation：职业技能，总和不超 EDU×20
- type=interest：兴趣技能，总和不超 INT×10
技能名须与标准 CoC 技能表一致（如：会计、人类学、攀爬、信用评级、闪避、急救、历史、图书馆使用、聆听、医学、神秘学、说服、心理学、侦查、潜行等）。
仅输出 JSON 数组，不要其它内容。"""
    user = f"职业：{occupation}\n职业技能点：{occ_pts}（EDU×20）\n兴趣技能点：{int_pts}（INT×10）\n请输出技能建议 JSON 数组。"
    raw = _call([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=temperature, max_tokens=2000, top_p=top_p)
    text = raw.strip()
    for p in ("```json", "```"):
        if text.startswith(p):
            text = text[len(p):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        arr = json.loads(text)
        if isinstance(arr, list):
            return [{"name": str(x.get("name", "")), "value": int(x.get("value", 0)), "type": str(x.get("type", "occupation"))} for x in arr if x.get("name")]
    except json.JSONDecodeError:
        pass
    return []


def generate_character_card(
    occupation: str = "",
    nationality: str = "",
    extra_hint: str = "",
    temperature: float = 0.9,
    top_p: float = 0.9,
) -> dict:
    """生成 CoC 人物卡。根据职业、国籍等生成完整人物卡 JSON。"""
    attrs = []
    for _ in range(8):
        v = coc_dice.roll_3d6()
        attrs.append(v)
    STR, CON, SIZ, DEX, INT, APP, POW, EDU = attrs

    SIZ = max(SIZ, 6)
    EDU = max(EDU, 6)
    SAN = POW * 5
    HP = (CON + SIZ) // 10
    MP = POW // 5
    total_siz_str = SIZ + STR
    if total_siz_str <= 64:
        DB, Build = -2, -2
    elif total_siz_str <= 84:
        DB, Build = -1, -1
    elif total_siz_str <= 124:
        DB, Build = 0, 0
    elif total_siz_str <= 164:
        DB, Build = 1, 1
    else:
        DB, Build = 2, 2
    MOVE = 8 if DEX >= SIZ else 7 if DEX < SIZ else 8

    occ = occupation.strip() or "调查员"
    nat = nationality.strip() or "美国"
    hint = extra_hint.strip()

    system = """你是一名克苏鲁的呼唤（CoC）跑团专家。根据给定的属性值和职业、国籍等要求，生成一张完整的人物卡 JSON。

输出要求：
- 必须输出纯 JSON，不要 markdown 包裹或其它说明
- 格式如下（严格按此结构）：
{
  "name": "角色名",
  "age": 25,
  "occupation": "职业",
  "nationality": "国籍",
  "attributes": {
    "STR": 数值, "CON": 数值, "SIZ": 数值, "DEX": 数值,
    "INT": 数值, "APP": 数值, "POW": 数值, "EDU": 数值,
    "SAN": 数值, "HP": 数值, "DB": 数值, "Build": 数值,
    "MOVE": 数值, "MP": 数值, "Luck": "投3D6×5"
  },
  "skills": [{"name": "技能名", "value": 百分比, "note": "可选备注"}],
  "combat": [{"name": "斗殴", "value": 百分比, "damage": "1D3或小刀1D4"}, {"name": "闪避", "value": 百分比}],
  "background": "背景故事，多段文字",
  "appearance": "形象描述",
  "traits": "特质描述",
  "beliefs": "思想与信念",
  "treasure": "宝贵之物"
}

- attributes 中的数值必须使用我提供的属性值，不要改动
- skills 需包含职业相关技能，总技能点按 EDU×20 + INT×10 分配（可略作调整）
- background 要具体、有故事感
- 仅使用标准克苏鲁的呼唤第七版规则：不包含人物肖像，不含通俗克苏鲁/通俗改编/英雄类型/天赋等扩展内容"""

    user = f"""职业：{occ}
国籍：{nat}
{f'额外要求：{hint}' if hint else ''}

已随机投骰得到的属性值：
STR={STR} CON={CON} SIZ={SIZ} DEX={DEX}
INT={INT} APP={APP} POW={POW} EDU={EDU}

请据此生成完整人物卡 JSON。attributes 必须完全使用上述数值；SAN={SAN} HP={HP} DB={DB} Build={Build} MOVE={MOVE} MP={MP}。只输出 JSON，不要其它内容。"""

    raw = _call(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        top_p=top_p,
    )
    text = raw.strip()
    for prefix in ("```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError("人物卡生成失败：模型未返回有效 JSON")

    if "attributes" not in data:
        data["attributes"] = {}
    data["attributes"].update({
        "STR": STR, "CON": CON, "SIZ": SIZ, "DEX": DEX,
        "INT": INT, "APP": APP, "POW": POW, "EDU": EDU,
        "SAN": SAN, "HP": HP, "DB": DB, "Build": Build,
        "MOVE": MOVE, "MP": MP, "Luck": "投3D6×5",
    })
    return data


def parse_text_to_character(raw_text: str) -> Optional[dict]:
    """用 LLM 将非结构化文本解析为人物卡 JSON。"""
    if not raw_text or len(raw_text.strip()) < 30:
        return None
    system = """你是 CoC 人物卡解析专家。将给定的调查员/人物卡文本解析为 JSON，仅使用标准克苏鲁的呼唤第七版规则。

输出要求：
- 仅输出一个 JSON 对象，不要 markdown 或其它说明
- 结构：{"name":"","age":0,"occupation":"","nationality":"","attributes":{"STR":0,"CON":0,"SIZ":0,"DEX":0,"INT":0,"APP":0,"POW":0,"EDU":0,"SAN":0,"HP":0,"DB":0,"Build":0,"MOVE":0,"MP":0,"Luck":"投3D6×5"},"skills":[{"name":"","value":0}],"combat":[{"name":"","value":0,"damage":""}],"background":"","appearance":"","traits":"","beliefs":"","treasure":""}
- 从文本中提取所有能识别的字段，数字用整数
- 若文本中无该字段，用 0 或空字符串
- 重要：若原文含「通俗调整」「通俗克苏鲁」「英雄类型」「天赋」等区块，一律舍弃，不要解析进 JSON。只保留标准规则下的属性、技能、战斗、背景等。"""

    user = f"请将以下人物卡文本解析为 JSON：\n\n{raw_text[:6000]}"
    try:
        raw = _call(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
            max_tokens=4000,
        )
    except Exception:
        return None
    text = raw.strip()
    for prefix in ("```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and (data.get("name") or data.get("attributes")):
            return data
    except json.JSONDecodeError:
        for m in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text):
            try:
                data = json.loads(m.group(0))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue
    return None


def infer_character_action(
    character_card: dict,
    chat_history: list[dict],
    script_context: str = "",
    temperature: float = 0.85,
    top_p: float = 0.9,
) -> str:
    """根据人物卡和当前剧情上下文，推断该角色会采取的下一步行动。"""
    system = """你是克苏鲁的呼唤（CoC）跑团中的角色扮演顾问。根据调查员的人物卡与当前剧情（KP 描述、场景、线索等），推断该角色在此时此地最可能采取的下一步行动。

要求：
- 行动需符合人物的性格、职业、技能与背景
- 考虑当前情境与已有线索，做出合理、有代入感的推断
- 输出简洁的行动描述，1-3 句话，可直接作为玩家输入发给 KP
- 不要输出 meta 说明（如「建议你……」），直接以角色视角描述行动
- 仅使用标准 CoC 规则，不含通俗克苏鲁"""

    char_summary = f"""角色：{character_card.get('name', '')}（{character_card.get('occupation', '')}）
背景/特质：{character_card.get('traits', '')}；信念：{character_card.get('beliefs', '')}
技能摘要：{json.dumps([s for s in (character_card.get('skills') or [])[:15]], ensure_ascii=False)}
属性：{json.dumps(character_card.get('attributes') or {}, ensure_ascii=False)}"""

    context_parts = []
    if script_context.strip():
        context_parts.append(f"【剧本相关】\n{script_context[:1500]}")
    if chat_history:
        recent = chat_history[-6:]
        ctx = "\n".join(f"{m.get('role','')}: {str(m.get('content',''))[:300]}" for m in recent)
        context_parts.append(f"【近期对话】\n{ctx}")

    user = f"""{char_summary}

---
{chr(10).join(context_parts) if context_parts else '（暂无剧情上下文，请给出该角色在调查开始时的典型开场行动）'}

---
请输出该角色下一步的行动描述（1-3 句，直接可发给 KP）："""

    return _call(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=500,
        temperature=temperature,
        top_p=top_p,
    )


def _load_kp_prompt() -> str:
    """加载 KP 预制 prompt：优先 data/coc/kp_prompt.txt，否则用 defaults/kp_prompt.txt。"""
    override = Path(config.COC_DATA_DIR) / "kp_prompt.txt"
    default = Path(config.DEFAULT_KP_PROMPT_PATH)
    if override.exists():
        return override.read_text(encoding="utf-8").strip()
    return default.read_text(encoding="utf-8").strip()


def _parse_and_execute_rolls(text: str, session_id: Optional[str] = None) -> str:
    """解析并执行 KP 回复中的 [ROLL:技能|值] 和 [DICE:expr]，替换为实际投骰结果。"""
    import coc_log
    def repl_roll(m):
        skill_name = m.group(1)
        try:
            val = int(m.group(2))
        except (TypeError, ValueError):
            val = 50
        success, roll_val, desc = coc_dice.roll_skill_check(val)
        result = f"【{skill_name}检定：{desc} → {'成功' if success else '失败'}】"
        if session_id:
            coc_log.append_log(session_id, {
                "type": "skill_check",
                "skill_value": val,
                "skill_name": skill_name,
                "roll": roll_val,
                "success": success,
                "description": desc,
            })
        return result

    def repl_dice(m):
        expr = m.group(1).strip()
        try:
            total, desc = coc_dice.roll(expr)
            result = f"【{desc} → {total}】"
        except ValueError:
            result = "【投骰格式错误】"
            total, desc = 0, ""
        if session_id and "格式错误" not in result:
            coc_log.append_log(session_id, {
                "type": "dice",
                "expr": expr,
                "result": total,
                "description": desc,
            })
        return result

    text = re.sub(r"\[ROLL:([^|]+)\|(\d+)\]", repl_roll, text)
    text = re.sub(r"\[DICE:([^\]]+)\]", repl_dice, text)
    return text


def kp_chat(
    script_context: str,
    chat_history: list[dict],
    user_message: str,
    character_card: Optional[dict],
    is_character_action: bool,
    session_id: Optional[str] = None,
    kp_prompt_override: Optional[str] = None,
    temperature: float = 0.85,
    top_p: float = 0.9,
) -> str:
    """KP 模式对话。"""
    system = (kp_prompt_override or _load_kp_prompt()).strip()

    parts = []
    if script_context.strip():
        parts.append(f"【剧本相关内容】\n{script_context}\n")
    if character_card and is_character_action:
        char_text = f"角色：{character_card.get('name','')}（{character_card.get('occupation','')}）\n"
        char_text += f"关键属性/技能摘要：{json.dumps(character_card.get('attributes',{}), ensure_ascii=False)}；技能：{json.dumps(character_card.get('skills',[])[:10], ensure_ascii=False)}\n"
        parts.append(f"【当前行动角色】\n{char_text}\n")
        parts.append("玩家以该角色身份进行行动/发言：")
    else:
        parts.append("【玩家向 KP 的询问】（未指定人物卡）：")

    parts.append(user_message)
    user_content = "\n".join(parts)

    messages = [{"role": "system", "content": system}]
    for h in chat_history[-20:]:
        messages.append({"role": h["role"], "content": h.get("content", "")})
    messages.append({"role": "user", "content": user_content})

    reply = _call(messages, max_tokens=4000, temperature=temperature, top_p=top_p)
    return _parse_and_execute_rolls(reply, session_id)
