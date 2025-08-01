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

DEFAULT_EXPERT_PROMPT = '''
Based on the provided transcript, make a detailed breakdown on the experts\' opinions with their name and position.
'''

DEFAULT_MARKET_PROMPT = '''
Based on the provided transcript and the experts\' opinions, summarize the direction of the market and suggestions on operation.
'''

DEFAULT_CATEGORIES = ["Finance", "Technology", "Education", "Entertainment", "News", "Sports", "Other"]
DEFAULT_TRANSCRIPT_LANGUAGE = os.getenv("DEFAULT_TRANSCRIPT_LANGUAGE", "en")
