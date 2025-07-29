import logging
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeService:
    def __init__(self, api_key):
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def get_video_metadata(self, video_url):
        try:
            video_id = video_url.split("v=")[1].split("&")[0]
            request = self.youtube.videos().list(part="snippet", id=video_id)
            response = request.execute()
            if response["items"]:
                snippet = response["items"][0]["snippet"]
                return {
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "publishedAt": snippet["publishedAt"]
                }
            else:
                logging.error(f"No video found for ID: {video_id}")
                return None
        except Exception as e:
            logging.error(f"Failed to get video metadata for {video_url}: {e}")
            return None

    def get_transcript(self, video_url):
        try:
            video_id = video_url.split("v=")[1].split("&")[0]
            logging.info(f"Attempting to fetch transcript for video ID: {video_id}")
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            transcript = "\n".join([item.text for item in transcript_list])
            return transcript
        except Exception as e:
            logging.error(f"Failed to get transcript for {video_url}: {e}")
            return None

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
        except Exception as e:
            logging.error(f"Gemini API video categorization failed: {e}")
            return "Error"

    def summarize_content(self, text, prompt):
        try:
            logging.info(f"Sending request to Gemini API with prompt: {prompt[:50]}...")
            response = self.model.generate_content(f"{prompt}\n\nTranscript:\n{text}")
            logging.info("Received response from Gemini API.")
            return response.text
        except Exception as e:
            logging.error(f"Gemini API summarization failed: {e}")
            return "Error: Could not generate summary."
