import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(name):
    api_key = os.getenv(name)
    if not api_key:
        raise ValueError(f"{name} environment variable not set.")
    return api_key

YOUTUBE_API_KEY = get_api_key("YOUTUBE_API_KEY")
GEMINI_API_KEY = get_api_key("GEMINI_API_KEY")
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH")

def _read_prompt_file(filename):
    with open(os.path.join(os.path.dirname(__file__), "prompts", filename), "r") as f:
        return f.read().strip()

DEFAULT_EXPERT_PROMPT = _read_prompt_file("expert_prompt.txt")
DEFAULT_MARKET_PROMPT = _read_prompt_file("market_prompt.txt")

DEFAULT_CATEGORIES = ["Finance", "Technology", "Education", "Entertainment", "News", "Sports", "Other"]
DEFAULT_TRANSCRIPT_LANGUAGE = os.getenv("DEFAULT_TRANSCRIPT_LANGUAGE", "en")
