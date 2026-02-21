"""配置：API Key 和 CoC 跑团相关。"""
import os


def get_api_key() -> str:
    """获取 API Key：优先 api_config（Web 配置），其次环境变量 BAILIAN_API_KEY。"""
    try:
        import api_config
        return api_config.get_api_key()
    except ImportError:
        pass
    return (os.getenv("BAILIAN_API_KEY", "") or "").strip()

# ---------- CoC 跑团 ----------
# 使用 Qwen3.5 Plus
MODEL_COC = "qwen3.5-plus"

# 数据目录
_BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(_BASE, "data")
COC_DATA_DIR = os.path.join(DATA_DIR, "coc")
COC_CHARACTERS_DIR = os.path.join(COC_DATA_DIR, "characters")
COC_SCRIPTS_DIR = os.path.join(COC_DATA_DIR, "scripts")
COC_SESSIONS_DIR = os.path.join(COC_DATA_DIR, "sessions")

# KP 预制 prompt：优先读 data/coc/kp_prompt.txt，否则用 defaults/kp_prompt.txt
DEFAULT_KP_PROMPT_PATH = os.path.join(_BASE, "defaults", "kp_prompt.txt")
