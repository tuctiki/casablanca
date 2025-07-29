import logging
from youtube_transcript_api import YouTubeTranscriptApi
import os
from googleapiclient.discovery import build

def get_video_metadata(video_url):
    try:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            logging.error("YOUTUBE_API_KEY environment variable not set.")
            raise ValueError("YOUTUBE_API_KEY environment variable not set.")

        youtube = build("youtube", "v3", developerKey=api_key)
        video_id = video_url.split("v=")[1].split("&")[0]

        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
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

def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        logging.info(f"Attempting to fetch transcript for video ID: {video_id}")
        api = YouTubeTranscriptApi()
        transcript_snippets = api.fetch(video_id)
        transcript = "\n".join([snippet.text for snippet in transcript_snippets])
        return transcript
    except Exception as e:
        logging.error(f"Failed to get transcript for {video_url}: {e}")
        return None