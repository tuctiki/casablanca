import sys
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        # Create an instance of YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        transcript_snippets = api.fetch(video_id)
        transcript_content = "\n".join([snippet.text for snippet in transcript_snippets])
        
        # Save transcript to a .txt file
        filename = f"{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_content)
            
        print(f"Transcript saved to {filename}")
        return transcript_content
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_transcript.py <youtube_video_url>")
    else:
        video_url = sys.argv[1]
        get_transcript(video_url)
