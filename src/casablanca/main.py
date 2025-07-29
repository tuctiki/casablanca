import sys
import os
import logging
import shutil
import argparse
from datetime import datetime
from dotenv import load_dotenv
from casablanca.transcript_utils import get_transcript, get_video_metadata
from casablanca.llm_utils import summarize_content, get_video_category

# Load environment variables from .env file
load_dotenv()

import sys
import os
import logging
import shutil
import argparse
from datetime import datetime
from dotenv import load_dotenv
from casablanca.transcript_utils import get_transcript, get_video_metadata
from casablanca.llm_utils import summarize_content, get_video_category

# Load environment variables from .env file
load_dotenv()

def configure_logging():
    if not logging.root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('casablanca.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

def clear_log_handlers():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def move_to_obsidian(video_title, video_date, expert_summary_path, market_summary_path):
    """Moves the generated markdown files to the Obsidian vault."""
    obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if not obsidian_path:
        logging.warning("OBSIDIAN_VAULT_PATH not set in .env file. Skipping move to Obsidian.")
        return

    # Sanitize video title for folder name
    sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    # Create a user-friendly folder name
    date_folder = video_date
    obsidian_dest_folder = os.path.expanduser(os.path.join(obsidian_path, date_folder, sanitized_title))
    
    os.makedirs(obsidian_dest_folder, exist_ok=True)

    # Move the files
    shutil.move(expert_summary_path, os.path.join(obsidian_dest_folder, "expert_summary.md"))
    shutil.move(market_summary_path, os.path.join(obsidian_dest_folder, "market_summary.md"))
    logging.info(f"Moved summary files to Obsidian vault: {obsidian_dest_folder}")

def run_casablanca(video_url, force=False):
    configure_logging()
    logging.info("Application started.")
    video_id = video_url.split("=")[-1]
    output_dir = os.path.join("outputs", video_id)
    os.makedirs(output_dir, exist_ok=True)

    transcript_path = os.path.join(output_dir, "transcript.txt")
    expert_summary_path = os.path.join(output_dir, "expert_summary.md")
    market_summary_path = os.path.join(output_dir, "market_summary.md")

    # Check if the final directory already exists in Obsidian
    if not force:
        obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")
        if obsidian_path:
            video_metadata = get_video_metadata(video_url)
            if video_metadata:
                video_title = video_metadata["title"]
                video_date = datetime.now().strftime("%Y-%m-%d")
                sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                date_folder = video_date
                obsidian_dest_folder = os.path.expanduser(os.path.join(obsidian_path, date_folder, sanitized_title))
                if os.path.exists(obsidian_dest_folder):
                    logging.info(f"Obsidian folder for {video_id} already exists. Skipping.")
                    logging.info("Application finished.")
                    return 0 # Indicate success and exit

    logging.info(f"Processing video URL: {video_url}")
    
    video_metadata = get_video_metadata(video_url)
    if not video_metadata:
        logging.error("Failed to get video metadata. Exiting.")
        logging.info("Application finished.")
        return 1 # Indicate error and exit

    video_title = video_metadata["title"]
    video_description = video_metadata["description"]
    video_date = datetime.now().strftime("%Y-%m-%d")
    logging.info(f"Video Title: {video_title}")
    logging.info(f"Video Description: {video_description[:100]}...") # Log first 100 chars of description

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

            move_to_obsidian(video_title, video_date, expert_summary_path, market_summary_path)

        else:
            logging.error("Failed to fetch transcript. Exiting summarization process.")
            return 1 # Indicate error
    else:
        logging.info(f"Video is not finance-related ({video_category}). Skipping transcript fetching and summarization.")
    logging.info("Application finished.")
    return 0 # Indicate success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process YouTube videos and summarize their content.')
    parser.add_argument('video_url', type=str, help='The URL of the YouTube video to process.')
    parser.add_argument('--force', action='store_true', help='Force reprocessing of the video even if it has been processed before.')
    args = parser.parse_args()

    sys.exit(run_casablanca(args.video_url, args.force))