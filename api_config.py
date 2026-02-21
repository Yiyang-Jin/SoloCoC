"""API 配置：支持 Web UI 配置，存储于 data/api_config.json。含多 LLM 接入（OpenAI 兼容）。"""
import os
import json
from pathlib import Path
from typing import Optional

import config

API_CONFIG_PATH = Path(config.DATA_DIR) / "api_config.json"

# 预设 LLM 提供商：base_url, 默认 model, 是否需要真实 API Key
# base_url 末尾不要加 /，OpenAI SDK 会自动拼接
LLM_PROVIDERS = {
    "bailian": {
        "name_zh": "阿里百炼",
        "name_en": "Alibaba Bailian",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "model": "qwen3.5-plus",
        "key_required": True,
        "key_env": "BAILIAN_API_KEY",
        "url_zh": "https://bailian.console.aliyun.com/",
        "url_en": "https://modelstudio.console.alibabacloud.com/",
    },
    "deepseek": {
        "name_zh": "DeepSeek",
        "name_en": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "key_required": True,
        "key_env": "DEEPSEEK_API_KEY",
        "url_zh": "https://platform.deepseek.com/",
        "url_en": "https://platform.deepseek.com/",
    },
    "moonshot": {
        "name_zh": "月之暗面 Kimi",
        "name_en": "Moonshot Kimi",
        "base_url": "https://api.moonshot.ai/v1",
        "model": "moonshot-v1-8k",
        "key_required": True,
        "key_env": "MOONSHOT_API_KEY",
        "url_zh": "https://platform.moonshot.ai/",
        "url_en": "https://platform.moonshot.ai/",
    },
    "zhipu": {
        "name_zh": "智谱 GLM",
        "name_en": "Zhipu GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-plus",
        "key_required": True,
        "key_env": "ZHIPU_API_KEY",
        "url_zh": "https://open.bigmodel.cn/",
        "url_en": "https://open.bigmodel.cn/",
    },
    "groq": {
        "name_zh": "Groq",
        "name_en": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-70b-versatile",
        "key_required": True,
        "key_env": "GROQ_API_KEY",
        "url_zh": "https://console.groq.com/",
        "url_en": "https://console.groq.com/",
    },
    "openai": {
        "name_zh": "OpenAI",
        "name_en": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_required": True,
        "key_env": "OPENAI_API_KEY",
        "url_zh": "https://platform.openai.com/",
        "url_en": "https://platform.openai.com/",
    },
    "openrouter": {
        "name_zh": "OpenRouter",
        "name_en": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "anthropic/claude-3.5-sonnet",
        "key_required": True,
        "key_env": "OPENROUTER_API_KEY",
        "url_zh": "https://openrouter.ai/",
        "url_en": "https://openrouter.ai/",
    },
    "together": {
        "name_zh": "Together.ai",
        "name_en": "Together.ai",
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Llama-3.1-70B-Instruct-Turbo",
        "key_required": True,
        "key_env": "TOGETHER_API_KEY",
        "url_zh": "https://api.together.xyz/",
        "url_en": "https://api.together.xyz/",
    },
    "ollama": {
        "name_zh": "Ollama（本地）",
        "name_en": "Ollama (Local)",
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5",
        "key_required": False,
        "placeholder_key": "ollama",
        "url_zh": "https://ollama.com/",
        "url_en": "https://ollama.com/",
    },
    "lmstudio": {
        "name_zh": "LM Studio（本地）",
        "name_en": "LM Studio (Local)",
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
        "key_required": False,
        "placeholder_key": "lm-studio",
        "url_zh": "https://lmstudio.ai/",
        "url_en": "https://lmstudio.ai/",
    },
    "custom": {
        "name_zh": "自定义",
        "name_en": "Custom",
        "base_url": "",
        "model": "",
        "key_required": True,
        "url_zh": "",
        "url_en": "",
    },
}


def _load() -> dict:
    if not API_CONFIG_PATH.exists():
        return {}
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict) -> None:
    Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(API_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_api_key() -> str:
    """获取 API Key：优先 Web 配置，其次环境变量。本地服务用 placeholder。"""
    data = _load()
    provider = (data.get("provider") or "bailian").strip()
    preset = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["bailian"])
    key = (data.get("api_key") or "").strip()
    if key:
        return key
    if not preset.get("key_required"):
        return preset.get("placeholder_key", "ollama")
    env_key = preset.get("key_env")
    if provider == "bailian" and not env_key:
        env_key = "BAILIAN_API_KEY"
    return (os.getenv(env_key or "", "") or "").strip()


def get_base_url() -> str:
    """获取 base_url。"""
    data = _load()
    provider = (data.get("provider") or "bailian").strip()
    custom_url = (data.get("base_url") or "").strip()
    if provider == "custom" and custom_url:
        return custom_url.rstrip("/")
    preset = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["bailian"])
    base = (preset.get("base_url") or "").strip()
    if data.get("base_url") and provider != "custom":
        base = (data.get("base_url") or base).strip()
    return base.rstrip("/") if base else ""


def get_model() -> str:
    """获取 model 名称。"""
    data = _load()
    provider = (data.get("provider") or "bailian").strip()
    custom_model = (data.get("model") or "").strip()
    preset = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["bailian"])
    default_model = (preset.get("model") or "").strip()
    if custom_model:
        return custom_model
    return default_model or "qwen3.5-plus"


def get_provider() -> str:
    """获取当前 provider id。"""
    data = _load()
    return (data.get("provider") or "bailian").strip()


def has_api_key() -> bool:
    """检查是否已配置有效 API Key（对需要 Key 的 provider）。"""
    provider = get_provider()
    preset = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["bailian"])
    if not preset.get("key_required"):
        return True
    return bool(get_api_key())


def get_full_config() -> dict:
    """获取完整配置（不返回 api_key 原文）。用于 Web UI。"""
    data = _load()
    provider = (data.get("provider") or "bailian").strip()
    preset = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["bailian"])
    base_url = (data.get("base_url") or preset.get("base_url") or "").strip()
    model = (data.get("model") or preset.get("model") or "").strip()
    return {
        "provider": provider,
        "base_url": base_url if provider == "custom" else (preset.get("base_url") or ""),
        "model": model or preset.get("model"),
        "api_key_set": bool((data.get("api_key") or "").strip()) or not preset.get("key_required"),
        "providers": [
            {"id": k, "name_zh": v.get("name_zh", k), "name_en": v.get("name_en", k)}
            for k, v in LLM_PROVIDERS.items()
        ],
    }


def set_config(provider: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None) -> None:
    """保存配置。"""
    data = _load()
    if provider is not None:
        data["provider"] = provider.strip()
    if base_url is not None:
        data["base_url"] = base_url.strip()
    if model is not None:
        data["model"] = model.strip()
    if api_key is not None:
        data["api_key"] = api_key.strip()
    _save(data)


def set_api_key(api_key: str) -> None:
    """仅保存 API Key（兼容旧逻辑）。"""
    data = _load()
    data["api_key"] = (api_key or "").strip()
    _save(data)
