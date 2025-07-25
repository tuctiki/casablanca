import sys
import os
import logging
from casablanca.transcript_utils import get_transcript
from casablanca.llm_utils import summarize_content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('casablanca.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == "__main__":
    logging.info("Application started.")
    if len(sys.argv) != 2:
        logging.info("Usage: python -m casablanca.main <youtube_video_url>")
        logging.info("Application exited due to incorrect usage.")
    else:
        video_url = sys.argv[1]
        logging.info(f"Processing video URL: {video_url}")
        transcript = get_transcript(video_url)

        if transcript:
            logging.info("Transcript fetched successfully. Proceeding with summarization.")
            expert_opinions_prompt = """
            Based on the provided transcript, make a detailed breakdown on the experts' opinions with their name and position.
            """

            market_direction_prompt = """
            Based on the provided transcript and the experts' opinions, summarize the direction of the market and suggestions on operation.
            """
            
            logging.info("Summarizing expert opinions...")
            expert_summary = summarize_content(transcript, expert_opinions_prompt)
            logging.info("\n--- Expert Opinions Summary ---\n")
            logging.info(expert_summary)

            logging.info("\nSummarizing market direction and operation suggestions...")
            market_summary = summarize_content(transcript, market_direction_prompt)
            logging.info("\n--- Market Direction and Operation Suggestions Summary ---\n")
            logging.info(market_summary)

            logging.info("\n[IMPORTANT] Ensure you have installed the Google Generative AI library (pip install google-generativeai) and set your GEMINI_API_KEY environment variable.")
        else:
            logging.error("Failed to fetch transcript. Exiting summarization process.")
    logging.info("Application finished.")