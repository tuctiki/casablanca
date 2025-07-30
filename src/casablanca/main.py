import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import click
from .transcript_utils import get_transcript, get_video_metadata
from .llm_utils import summarize_content, get_video_category
from .file_utils import move_to_obsidian
from .config import OBSIDIAN_VAULT_PATH, DEFAULT_EXPERT_PROMPT, DEFAULT_MARKET_PROMPT, DEFAULT_CATEGORIES

def configure_logging(log_level):
    # Clear existing handlers to prevent duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.root.addHandler(console_handler)

    # Set up file handler with rotation
    file_handler = RotatingFileHandler('casablanca.log', maxBytes=1024*1024*5, backupCount=5) # 5 MB per file, 5 backup files
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.root.addHandler(file_handler)

    # Set the logging level
    logging.root.setLevel(getattr(logging, log_level.upper()))

@click.command()
@click.argument('video_url', type=str)
@click.option('--force', is_flag=True, help='Force reprocessing of the video even if it has been processed before.')
@click.option('--expert-prompt', default=DEFAULT_EXPERT_PROMPT, help='Custom prompt for expert opinions summary.')
@click.option('--market-prompt', default=DEFAULT_MARKET_PROMPT, help='Custom prompt for market direction summary.')
@click.option('--categories', default=','.join(DEFAULT_CATEGORIES), help='Comma-separated list of categories for video classification.')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False), help='Set the logging level.')
def cli(video_url, force, expert_prompt, market_prompt, categories, log_level):
    configure_logging(log_level)
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
        sys.exit(1)

    logging.debug(f"Video metadata: {video_metadata}")

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
            sys.exit(0)

    logging.info(f"Processing video URL: {video_url}")
    logging.info(f"Video Title: {video_title}")
    logging.info(f"Video Description: {video_description[:100]}...")

    categories_list = [c.strip() for c in categories.split(',')]
    logging.debug(f"Using categories: {categories_list}")
    video_category = get_video_category(video_title, video_description, categories_list)
    logging.info(f"Video Category: {video_category}")

    if video_category in ["Finance", "News"]:
        logging.info("Video is finance-related. Proceeding with transcript fetching and summarization.")
        transcript = get_transcript(video_url)

        if transcript:
            transcript_path = os.path.join(output_dir, "transcript.txt")
            with open(transcript_path, "w") as f:
                f.write(transcript)
            logging.info(f"Transcript saved to {transcript_path}")
            logging.debug(f"Transcript content (first 100 chars): {transcript[:100]}...")

            logging.info("Summarizing expert opinions...")
            expert_summary = summarize_content(transcript, expert_prompt)
            with open(expert_summary_path, "w") as f:
                f.write(expert_summary)
            logging.info(f"Expert summary saved to {expert_summary_path}")
            logging.debug(f"Expert summary content (first 100 chars): {expert_summary[:100]}...")

            logging.info("Summarizing market direction and operation suggestions...")
            market_summary = summarize_content(transcript, market_prompt)
            with open(market_summary_path, "w") as f:
                f.write(market_summary)
            logging.info(f"Market summary saved to {market_summary_path}")
            logging.debug(f"Market summary content (first 100 chars): {market_summary[:100]}...")

            move_to_obsidian(video_title, video_date, expert_summary_path, market_summary_path, OBSIDIAN_VAULT_PATH)

        else:
            logging.error("Failed to fetch transcript. Exiting summarization process.")
            sys.exit(1)
    else:
        logging.info(f"Video is not finance-related ({video_category}). Skipping transcript fetching and summarization.")
    logging.info("Application finished.")
    sys.exit(0)

if __name__ == "__main__":
    cli()