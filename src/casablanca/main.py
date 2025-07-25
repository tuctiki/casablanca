import sys
import os
from casablanca.transcript_utils import get_transcript
from casablanca.llm_utils import summarize_content

if __name__ == "__main__":
    print("[LOG] Application started.")
    if len(sys.argv) != 2:
        print("Usage: python -m casablanca.main <youtube_video_url>")
        print("[LOG] Application exited due to incorrect usage.")
    else:
        video_url = sys.argv[1]
        print(f"[LOG] Processing video URL: {video_url}")
        transcript = get_transcript(video_url)

        if transcript:
            print("[LOG] Transcript fetched successfully. Proceeding with summarization.")
            expert_opinions_prompt = """
            Based on the provided transcript, make a detailed breakdown on the experts' opinions with their name and position.
            """

            market_direction_prompt = """
            Based on the provided transcript and the experts' opinions, summarize the direction of the market and suggestions on operation.
            """
            
            print("[LOG] Summarizing expert opinions...")
            expert_summary = summarize_content(transcript, expert_opinions_prompt)
            print("\n--- Expert Opinions Summary ---\n")
            print(expert_summary)

            print("\n[LOG] Summarizing market direction and operation suggestions...")
            market_summary = summarize_content(transcript, market_direction_prompt)
            print("\n--- Market Direction and Operation Suggestions Summary ---\n")
            print(market_summary)

            print("\n[IMPORTANT] Ensure you have installed the Google Generative AI library (pip install google-generativeai) and set your GEMINI_API_KEY environment variable.")
        else:
            print("[ERROR] Failed to fetch transcript. Exiting summarization process.")
    print("[LOG] Application finished.")