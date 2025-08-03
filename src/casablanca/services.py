import logging
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from datetime import datetime

from .config import DEFAULT_TRANSCRIPT_LANGUAGE
from .url_utils import extract_video_id
from .exceptions import VideoMetadataError, TranscriptError, GeminiServiceError
from .models import Video

class YouTubeService:
    def __init__(self, api_key):
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def get_video_metadata(self, video_url):
        try:
            video_id = extract_video_id(video_url)
            if not video_id:
                logging.error(f"Invalid video URL: {video_url}")
                raise VideoMetadataError(f"Invalid video URL: {video_url}")
            request = self.youtube.videos().list(part="snippet", id=video_id)
            response = request.execute()
            if response["items"]:
                snippet = response["items"][0]["snippet"]
                return Video(
                    title=snippet["title"],
                    description=snippet["description"],
                    published_at=datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                )
            else:
                logging.error(f"No video found for ID: {video_id}")
                raise VideoMetadataError(f"No video found for ID: {video_id}")
        except HttpError as e:
            logging.error(f"HTTP error fetching video metadata for {video_url}: {e}")
            raise VideoMetadataError(f"HTTP error fetching video metadata for {video_url}: {e}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred while fetching video metadata for {video_url}: {e}")
            raise VideoMetadataError(f"An unexpected error occurred while fetching video metadata for {video_url}: {e}") from e

    def get_transcript(self, video_url):
        try:
            video_id = extract_video_id(video_url)
            logging.info(f"Attempting to fetch transcript for video ID: {video_id}")
            transcript_list = YouTubeTranscriptApi().list(video_id)
            transcript = transcript_list.find_transcript([DEFAULT_TRANSCRIPT_LANGUAGE])
            transcript_data = transcript.fetch()
            transcript_text = "\n".join([item.text for item in transcript_data.snippets])
            return transcript_text
        except (NoTranscriptFound, TranscriptsDisabled) as e:
            logging.error(f"Transcript not available for {video_url}: {e}")
            raise TranscriptError(f"Transcript not available for {video_url}: {e}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred while fetching transcript for {video_url}: {e}")
            raise TranscriptError(f"An unexpected error occurred while fetching transcript for {video_url}: {e}") from e

class GeminiService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_video_category(self, title, description, categories):
        try:
            category_list_str = ", ".join(categories)
            prompt = f"""
            Given the following video title and description, classify the video into one of these categories: {category_list_str}.
            If none of the categories apply, respond with "Other".
            Respond with only the category name.

            Title: {title}
            Description: {description}
            """
            logging.info("Sending request to Gemini API for video categorization...")
            response = self.model.generate_content(prompt)
            logging.info("Received response from Gemini API for video categorization.")
            return response.text.strip()
        except genai.types.BlockedPromptException as e:
            logging.error(f"Gemini API video categorization failed due to blocked prompt: {e}")
            raise GeminiServiceError(f"Gemini API video categorization failed due to blocked prompt: {e}") from e
        except genai.types.StopCandidateException as e:
            logging.error(f"Gemini API video categorization failed due to stop candidate: {e}")
            raise GeminiServiceError(f"Gemini API video categorization failed due to stop candidate: {e}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred during Gemini API video categorization: {e}")
            raise GeminiServiceError(f"An unexpected error occurred during Gemini API video categorization: {e}") from e

    def summarize_content(self, text, prompt):
        try:
            logging.info(f"Sending request to Gemini API with prompt: {prompt[:50]}...")
            response = self.model.generate_content(f"{prompt}\n\nTranscript:\n{text}")
            logging.info("Received response from Gemini API.")
            return response.text
        except Exception as e:
            logging.error(f"Gemini API summarization failed: {e}")
            raise GeminiServiceError(f"Gemini API summarization failed: {e}") from e