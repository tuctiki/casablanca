
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
