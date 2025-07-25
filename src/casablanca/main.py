import sys
import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        api = YouTubeTranscriptApi()
        transcript_snippets = api.fetch(video_id)
        transcript_content = "\n".join([snippet.text for snippet in transcript_snippets])
        
        filename = f"{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_content)
            
        print(f"[LOG] Transcript saved to {filename}")
        return transcript_content
    except Exception as e:
        print(f"[ERROR] Failed to get transcript: {e}")
        return None

def summarize_content(text, prompt):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash') # Using the specified model
        print(f"[LOG] Sending request to Gemini API for prompt: {prompt[:50]}...")
        response = model.generate_content(f"{prompt}\n\nTranscript:\n{text}")
        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini API summarization failed: {e}")
        return "Error: Could not generate summary."

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m casablanca.main <youtube_video_url>")
    else:
        video_url = sys.argv[1]
        print(f"[LOG] Fetching transcript for {video_url}")
        transcript = get_transcript(video_url)

        if transcript:
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