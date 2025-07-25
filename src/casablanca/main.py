import sys
import os
import logging
from casablanca.transcript_utils import get_transcript, get_video_metadata
from casablanca.llm_utils import summarize_content, get_video_category

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
        video_id = video_url.split("=")[-1]
        output_dir = os.path.join("outputs", video_id)
        os.makedirs(output_dir, exist_ok=True)

        logging.info(f"Processing video URL: {video_url}")
        
        video_metadata = get_video_metadata(video_url)
        if not video_metadata:
            logging.error("Failed to get video metadata. Exiting.")
            logging.info("Application finished.")
            sys.exit(1)

        video_title = video_metadata["title"]
        video_description = video_metadata["description"]
        logging.info(f"Video Title: {video_title}")
        logging.info(f"Video Description: {video_description[:100]}...") # Log first 100 chars of description

        categories = ["Finance", "Technology", "Education", "Entertainment", "News", "Sports", "Other"]
        video_category = get_video_category(video_title, video_description, categories)
        logging.info(f"Video Category: {video_category}")

        if video_category == "Finance":
            logging.info("Video is finance-related. Proceeding with transcript fetching and summarization.")
            transcript = get_transcript(video_url)

            if transcript:
                transcript_path = os.path.join(output_dir, "transcript.txt")
                with open(transcript_path, "w") as f:
                    f.write(transcript)
                logging.info(f"Transcript saved to {transcript_path}")

                expert_opinions_prompt = """
                Based on the provided transcript, make a detailed breakdown on the experts' opinions with their name and position.
                """

                market_direction_prompt = """
                Based on the provided transcript and the experts' opinions, summarize the direction of the market and suggestions on operation.
                """

                logging.info("Summarizing expert opinions...")
                expert_summary = summarize_content(transcript, expert_opinions_prompt)
                expert_summary_path = os.path.join(output_dir, "expert_summary.md")
                with open(expert_summary_path, "w") as f:
                    f.write(expert_summary)
                logging.info(f"Expert summary saved to {expert_summary_path}")

                logging.info("Summarizing market direction and operation suggestions...")
                market_summary = summarize_content(transcript, market_direction_prompt)
                market_summary_path = os.path.join(output_dir, "market_summary.md")
                with open(market_summary_path, "w") as f:
                    f.write(market_summary)
                logging.info(f"Market summary saved to {market_summary_path}")

            else:
                logging.error("Failed to fetch transcript. Exiting summarization process.")
        else:
            logging.info(f"Video is not finance-related ({video_category}). Skipping transcript fetching and summarization.")
    logging.info("Application finished.")