import pytest
from unittest.mock import patch, MagicMock
from casablanca.services import YouTubeService, GeminiService
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled
import google.generativeai as genai
from googleapiclient.discovery import build

# Mock API keys for testing
MOCK_YOUTUBE_API_KEY = "mock_youtube_api_key"
MOCK_GEMINI_API_KEY = "mock_gemini_api_key"

@pytest.fixture
def youtube_service():
    with patch('casablanca.services.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        service = YouTubeService(MOCK_YOUTUBE_API_KEY)
        yield service, mock_build, mock_youtube

@pytest.fixture
def gemini_service():
    with patch('google.generativeai.GenerativeModel') as mock_generative_model:
        with patch('google.generativeai.configure') as mock_configure:
            service = GeminiService(MOCK_GEMINI_API_KEY)
            yield service, mock_generative_model, mock_configure

# YouTubeService Tests

def test_youtube_service_get_video_metadata_success(youtube_service):
    service, mock_build, mock_youtube = youtube_service
    mock_youtube.videos.return_value.list.return_value.execute.return_value = {
        "items": [{
            "snippet": {
                "title": "Test Title",
                "description": "Test Description",
                "publishedAt": "2023-10-26T12:00:00Z"
            }
        }]
    }
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    metadata = service.get_video_metadata(video_url)

    assert metadata["title"] == "Test Title"
    assert metadata["description"] == "Test Description"
    assert metadata["publishedAt"] == "2023-10-26T12:00:00Z"
    mock_build.assert_called_once_with("youtube", "v3", developerKey=MOCK_YOUTUBE_API_KEY)
    mock_youtube.videos.return_value.list.assert_called_once_with(part="snippet", id="test_video_id")

def test_youtube_service_get_video_metadata_no_video_found(youtube_service):
    service, mock_build, mock_youtube = youtube_service
    mock_youtube.videos.return_value.list.return_value.execute.return_value = {"items": []}
    video_url = "https://www.youtube.com/watch?v=non_existent_id"
    metadata = service.get_video_metadata(video_url)
    assert metadata is None

def test_youtube_service_get_video_metadata_api_error(youtube_service):
    service, mock_build, mock_youtube = youtube_service
    mock_youtube.videos.return_value.list.return_value.execute.side_effect = Exception("API Error")
    video_url = "https://www.youtube.com/watch?v=error_id"
    metadata = service.get_video_metadata(video_url)
    assert metadata is None

def test_youtube_service_get_video_metadata_invalid_url(youtube_service):
    service, mock_build, mock_youtube = youtube_service
    video_url = "invalid_url"
    metadata = service.get_video_metadata(video_url)
    assert metadata is None
    mock_build.assert_called_once_with("youtube", "v3", developerKey=MOCK_YOUTUBE_API_KEY)
    mock_youtube.videos.return_value.list.assert_not_called()

@patch('casablanca.services.YouTubeTranscriptApi')
def test_youtube_service_get_transcript_success(mock_youtube_transcript_api, youtube_service):
    service, _, _ = youtube_service
    mock_transcript_list = MagicMock()
    mock_transcript = MagicMock()
    mock_youtube_transcript_api.return_value.list.return_value = mock_transcript_list
    mock_transcript_list.find_transcript.return_value = mock_transcript
    
    class MockSnippet:
        def __init__(self, text):
            self.text = text
    mock_transcript_data = MagicMock()
    mock_transcript_data.snippets = [MockSnippet('Hello'), MockSnippet('World')]
    mock_transcript.fetch.return_value = mock_transcript_data
    
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    transcript = service.get_transcript(video_url)
    assert transcript == "Hello\nWorld"
    mock_youtube_transcript_api.return_value.list.assert_called_once_with("test_video_id")
    mock_transcript_list.find_transcript.assert_called_once_with(['en'])
    mock_transcript.fetch.assert_called_once()

@patch('casablanca.services.YouTubeTranscriptApi')
def test_youtube_service_get_transcript_no_transcript_found(mock_youtube_transcript_api, youtube_service):
    service, _, _ = youtube_service
    mock_youtube_transcript_api.return_value.list.side_effect = NoTranscriptFound("test_video_id", ["en"], [])
    video_url = "https://www.youtube.com/watch?v=no_transcript_id"
    transcript = service.get_transcript(video_url)
    assert transcript is None

@patch('casablanca.services.YouTubeTranscriptApi')
def test_youtube_service_get_transcript_transcripts_disabled(mock_youtube_transcript_api, youtube_service):
    service, _, _ = youtube_service
    mock_youtube_transcript_api.return_value.list.side_effect = TranscriptsDisabled("test_video_id")
    video_url = "https://www.youtube.com/watch?v=disabled_transcript_id"
    transcript = service.get_transcript(video_url)
    assert transcript is None

@patch('casablanca.services.YouTubeTranscriptApi')
def test_youtube_service_get_transcript_other_exception(mock_youtube_transcript_api, youtube_service):
    service, _, _ = youtube_service
    mock_youtube_transcript_api.return_value.list.side_effect = Exception("Some other error")
    video_url = "https://www.youtube.com/watch?v=error_id"
    transcript = service.get_transcript(video_url)
    assert transcript is None


def test_youtube_service_get_transcript_invalid_url(youtube_service):
    service, _, _ = youtube_service
    video_url = "invalid_url"
    transcript = service.get_transcript(video_url)
    assert transcript is None

# GeminiService Tests

def test_gemini_service_get_video_category_success(gemini_service):
    service, mock_generative_model, mock_configure = gemini_service
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.return_value.text = "Finance"
    title = "Video Title"
    description = "Video Description"
    categories = ["Finance", "News"]
    category = service.get_video_category(title, description, categories)
    assert category == "Finance"
    mock_configure.assert_called_once_with(api_key=MOCK_GEMINI_API_KEY)
    mock_generative_model.assert_called_once_with('gemini-1.5-flash')
    mock_model_instance.generate_content.assert_called_once()

def test_gemini_service_get_video_category_api_failure(gemini_service):
    service, mock_generative_model, _ = gemini_service
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.side_effect = Exception("API Error")
    title = "Video Title"
    description = "Video Description"
    categories = ["Finance", "News"]
    category = service.get_video_category(title, description, categories)
    assert category == "Error"

def test_gemini_service_summarize_content_success(gemini_service):
    service, mock_generative_model, mock_configure = gemini_service
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.return_value.text = "This is a summary."
    text = "Some long text."
    prompt = "Summarize this."
    summary = service.summarize_content(text, prompt)
    assert summary == "This is a summary."
    mock_configure.assert_called_once_with(api_key=MOCK_GEMINI_API_KEY)
    mock_generative_model.assert_called_once_with('gemini-1.5-flash')
    mock_model_instance.generate_content.assert_called_once()

def test_gemini_service_summarize_content_api_failure(gemini_service):
    service, mock_generative_model, _ = gemini_service
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.side_effect = Exception("API Error")
    text = "Some long text."
    prompt = "Summarize this."
    summary = service.summarize_content(text, prompt)
    assert summary == "Error: Could not generate summary."
