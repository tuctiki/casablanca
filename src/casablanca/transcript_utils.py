from .services import YouTubeService
from .config import YOUTUBE_API_KEY
import logging

youtube_service = YouTubeService(YOUTUBE_API_KEY)

def get_video_metadata(video_url):
    try:
        return youtube_service.get_video_metadata(video_url)
    except Exception as e:
        logging.error(f"Error in get_video_metadata: {e}")
        return None

def get_transcript(video_url):
    try:
        return youtube_service.get_transcript(video_url)
    except Exception as e:
        logging.error(f"Error in get_transcript: {e}")
        return None