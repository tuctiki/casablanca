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
        video_id = video_url.split("=")[-1]
        output_dir = os.path.join("outputs", video_id)
        os.makedirs(output_dir, exist_ok=True)

        logging.info(f"Processing video URL: {video_url}")
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
    logging.info("Application finished.")