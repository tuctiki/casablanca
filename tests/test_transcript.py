import sys
from youtube_transcript_api import YouTubeTranscriptApi

print(f"Module loaded from: {YouTubeTranscriptApi.__module__}")
print(f"File loaded from: {YouTubeTranscriptApi.__file__}")

try:
    transcript = YouTubeTranscriptApi.get_transcript('erI6k_hnToE')
    print("Transcript fetched successfully (first 3 entries):")
    for i, entry in enumerate(transcript[:3]):
        print(entry)
except Exception as e:
    print(f"Error in test_transcript.py: {e}")