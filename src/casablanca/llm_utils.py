from .services import GeminiService
from .config import GEMINI_API_KEY
import logging

gemini_service = GeminiService(GEMINI_API_KEY)

def get_video_category(title, description, categories):
    try:
        return gemini_service.get_video_category(title, description, categories)
    except Exception as e:
        logging.error(f"Error in get_video_category: {e}")
        return "Error"

def summarize_content(text, prompt):
    try:
        return gemini_service.summarize_content(text, prompt)
    except Exception as e:
        logging.error(f"Error in summarize_content: {e}")
        return "Error: Could not generate summary."