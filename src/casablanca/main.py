import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import click

from .config import OBSIDIAN_VAULT_PATH, DEFAULT_EXPERT_PROMPT, DEFAULT_MARKET_PROMPT, DEFAULT_CATEGORIES, YOUTUBE_API_KEY, GEMINI_API_KEY
from .services import YouTubeService, GeminiService
from .exceptions import VideoMetadataError, TranscriptError
from .processor import VideoProcessor

def configure_logging(log_level):
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
    youtube_service = YouTubeService(YOUTUBE_API_KEY)
    gemini_service = GeminiService(GEMINI_API_KEY)
    processor = VideoProcessor(youtube_service, gemini_service, OBSIDIAN_VAULT_PATH, DEFAULT_CATEGORIES)
    try:
        processor.process(video_url, force, expert_prompt, market_prompt, categories)
    except (VideoMetadataError, TranscriptError, GeminiServiceError) as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Application finished.")
    sys.exit(0)

if __name__ == "__main__":
    cli()
