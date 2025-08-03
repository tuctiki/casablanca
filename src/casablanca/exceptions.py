class VideoMetadataError(Exception):
    """Custom exception for errors related to video metadata retrieval."""
    pass

class TranscriptError(Exception):
    """Custom exception for errors related to transcript fetching."""
    pass

class GeminiServiceError(Exception):
    """Custom exception for errors related to Gemini API service."""
    pass