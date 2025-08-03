import logging
import os
from .file_utils import move_to_obsidian, sanitize_title, generate_output_paths
from .exceptions import VideoMetadataError, TranscriptError
from .models import Video


class VideoProcessor:
    def __init__(self, youtube_service, gemini_service, obsidian_vault_path, default_categories):
        self.youtube_service = youtube_service
        self.gemini_service = gemini_service
        self.obsidian_vault_path = obsidian_vault_path
        self.default_categories = default_categories

    def _get_video_info(self, video_url) -> Video:
        video = self.youtube_service.get_video_metadata(video_url)
        if not video:
            raise VideoMetadataError("Failed to get video metadata.")

        logging.debug(f"Video metadata: {video}")
        return video

    def _check_existing_output(self, video_id, video: Video, force):
        if not force and self.obsidian_vault_path:
            sanitized_title = sanitize_title(video.title)
            date_folder = video.date
            obsidian_dest_folder = os.path.expanduser(os.path.join(self.obsidian_vault_path, date_folder, sanitized_title))
            if os.path.exists(obsidian_dest_folder):
                logging.info(f"Obsidian folder for {video_id} already exists. Skipping.")
                return True
        return False

    def _classify_video(self, video_title, video_description, categories):
        try:
            categories_list = [c.strip() for c in categories.split(',')]
            logging.debug(f"Using categories: {categories_list}")
            video_category = self.gemini_service.get_video_category(video_title, video_description, categories_list)
            logging.info(f"Video Category: {video_category}")
            return video_category
        except GeminiServiceError as e:
            logging.error(f"Video classification failed: {e}")
            raise

    def _process_finance_video(self, video_url, output_dir, expert_summary_path, market_summary_path, expert_prompt, market_prompt, video: Video):
        logging.info("Video is finance-related. Proceeding with transcript fetching and summarization.")
        transcript = self.youtube_service.get_transcript(video_url)

        if not transcript:
            raise TranscriptError("Failed to fetch transcript. Exiting summarization process.")

        transcript_path = os.path.join(output_dir, "transcript.txt")
        with open(transcript_path, "w") as f:
            f.write(transcript)
        logging.info(f"Transcript saved to {transcript_path}")
        logging.debug(f"Transcript content (first 100 chars): {transcript[:100]}...")

        logging.info("Summarizing expert opinions...")
        expert_summary = self.gemini_service.summarize_content(transcript, expert_prompt)
        with open(expert_summary_path, "w") as f:
            f.write(expert_summary)
        logging.info(f"Expert summary saved to {expert_summary_path}")
        logging.debug(f"Expert summary content (first 100 chars): {expert_summary[:100]}...")

        logging.info("Summarizing market direction and operation suggestions...")
        market_summary = self.gemini_service.summarize_content(transcript, market_prompt)
        with open(market_summary_path, "w") as f:
            f.write(market_summary)
        logging.info(f"Market summary saved to {market_summary_path}")
        logging.debug(f"Market summary content (first 100 chars): {market_summary[:100]}...")

        move_to_obsidian(video, expert_summary_path, market_summary_path, self.obsidian_vault_path)

    def process(self, video_url, force, expert_prompt, market_prompt, categories):
        from .url_utils import extract_video_id
        video_id = extract_video_id(video_url)
        output_dir, expert_summary_path, market_summary_path = generate_output_paths(video_id)

        video = self._get_video_info(video_url)

        if self._check_existing_output(video_id, video, force):
            return

        logging.info(f"Processing video URL: {video_url}")
        logging.info(f"Video Title: {video.title}")
        logging.info(f"Video Description: {video.description[:100]}...")

        video_category = self._classify_video(video.title, video.description, categories)

        if video_category in ["Finance", "News"]:
            self._process_finance_video(video_url, output_dir, expert_summary_path, market_summary_path, expert_prompt, market_prompt, video)
        else:
            logging.info(f"Video is not finance-related ({video_category}). Skipping transcript fetching and summarization.")
