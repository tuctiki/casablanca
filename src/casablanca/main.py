import sys
import os
import logging
import argparse
from datetime import datetime
from .transcript_utils import get_transcript, get_video_metadata
from .llm_utils import summarize_content, get_video_category
from .file_utils import move_to_obsidian
from .config import OBSIDIAN_VAULT_PATH

def configure_logging():
    # Clear existing handlers to prevent duplicate logs in tests
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    if not logging.root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('casablanca.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

def run_casablanca(video_url, force=False):
    configure_logging()
    logging.info("Application started.")
    video_id = video_url.split("=")[-1]
    output_dir = os.path.join("outputs", video_id)
    os.makedirs(output_dir, exist_ok=True)

    expert_summary_path = os.path.join(output_dir, "expert_summary.md")
    market_summary_path = os.path.join(output_dir, "market_summary.md")

    video_metadata = get_video_metadata(video_url)
    if not video_metadata:
        logging.error("Failed to get video metadata. Exiting.")
        logging.info("Application finished.")
        return 1

    video_title = video_metadata["title"]
    video_description = video_metadata["description"]
    video_date = datetime.strptime(video_metadata["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

    if not force and OBSIDIAN_VAULT_PATH:
        sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        date_folder = video_date
        obsidian_dest_folder = os.path.expanduser(os.path.join(OBSIDIAN_VAULT_PATH, date_folder, sanitized_title))
        if os.path.exists(obsidian_dest_folder):
            logging.info(f"Obsidian folder for {video_id} already exists. Skipping.")
            logging.info("Application finished.")
            return 0

    logging.info(f"Processing video URL: {video_url}")
    logging.info(f"Video Title: {video_title}")
    logging.info(f"Video Description: {video_description[:100]}...")

    categories = ["Finance", "Technology", "Education", "Entertainment", "News", "Sports", "Other"]
    video_category = get_video_category(video_title, video_description, categories)
    logging.info(f"Video Category: {video_category}")

    if video_category in ["Finance", "News"]:
        logging.info("Video is finance-related. Proceeding with transcript fetching and summarization.")
        transcript = get_transcript(video_url)

        if transcript:
            transcript_path = os.path.join(output_dir, "transcript.txt")
            with open(transcript_path, "w") as f:
                f.write(transcript)
            logging.info(f"Transcript saved to {transcript_path}")

            expert_opinions_prompt = '''
            Based on the provided transcript, make a detailed breakdown on the experts\' opinions with their name and position.
            '''

            market_direction_prompt = '''
            Based on the provided transcript and the experts\' opinions, summarize the direction of the market and suggestions on operation.
            '''

            logging.info("Summarizing expert opinions...")
            expert_summary = summarize_content(transcript, expert_opinions_prompt)
            with open(expert_summary_path, "w") as f:
                f.write(expert_summary)
            logging.info(f"Expert summary saved to {expert_summary_path}")

            logging.info("Summarizing market direction and operation suggestions...")
            market_summary = summarize_content(transcript, market_direction_prompt)
            with open(market_summary_path, "w") as f:
                f.write(market_summary)
            logging.info(f"Market summary saved to {market_summary_path}")

            move_to_obsidian(video_title, video_date, expert_summary_path, market_summary_path, OBSIDIAN_VAULT_PATH)

        else:
            logging.error("Failed to fetch transcript. Exiting summarization process.")
            return 1
    else:
        logging.info(f"Video is not finance-related ({video_category}). Skipping transcript fetching and summarization.")
    logging.info("Application finished.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process YouTube videos and summarize their content.')
    parser.add_argument('video_url', type=str, help='The URL of the YouTube video to process.')
    parser.add_argument('--force', action='store_true', help='Force reprocessing of the video even if it has been processed before.')
    args = parser.parse_args()

    sys.exit(run_casablanca(args.video_url, args.force))