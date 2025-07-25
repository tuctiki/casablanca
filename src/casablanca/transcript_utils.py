from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        print(f"[LOG] Attempting to fetch transcript for video ID: {video_id}")
        api = YouTubeTranscriptApi()
        transcript_snippets = api.fetch(video_id)
        transcript_content = "\n".join([snippet['text'] for snippet in transcript_snippets])
        
        filename = f"{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_content)
            
        print(f"[LOG] Transcript successfully saved to {filename}")
        return transcript_content
    except Exception as e:
        print(f"[ERROR] Failed to get transcript for {video_url}: {e}")
        return None