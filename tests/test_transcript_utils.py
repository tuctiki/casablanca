import pytest
from unittest.mock import patch, MagicMock
from casablanca.transcript_utils import get_transcript, get_video_metadata
from casablanca.services import YouTubeService
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_transcript_success(mock_youtube_service):
    mock_youtube_service.get_transcript.return_value = "Hello\nWorld"

    video_url = "https://www.youtube.com/watch?v=test_video_id"
    transcript = get_transcript(video_url)

    assert transcript == "Hello\nWorld"
    mock_youtube_service.get_transcript.assert_called_once_with(video_url)

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_transcript_no_transcript_found(mock_youtube_service):
    mock_youtube_service.get_transcript.side_effect = NoTranscriptFound("test_video_id", ["en"], [])

    video_url = "https://www.youtube.com/watch?v=no_transcript_id"
    transcript = get_transcript(video_url)

    assert transcript is None

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_transcript_transcripts_disabled(mock_youtube_service):
    mock_youtube_service.get_transcript.side_effect = TranscriptsDisabled("test_video_id")

    video_url = "https://www.youtube.com/watch?v=disabled_transcript_id"
    transcript = get_transcript(video_url)

    assert transcript is None

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_transcript_other_exception(mock_youtube_service):
    mock_youtube_service.get_transcript.side_effect = Exception("Some other error")

    video_url = "https://www.youtube.com/watch?v=error_id"
    transcript = get_transcript(video_url)

    assert transcript is None

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_video_metadata_success(mock_youtube_service):
    mock_youtube_service.get_video_metadata.return_value = {"title": "Test Title", "description": "Test Description", "publishedAt": "2023-10-26T12:00:00Z"}

    video_url = "https://www.youtube.com/watch?v=test_video_id"
    metadata = get_video_metadata(video_url)

    assert metadata["title"] == "Test Title"
    assert metadata["description"] == "Test Description"
    assert metadata["publishedAt"] == "2023-10-26T12:00:00Z"
    mock_youtube_service.get_video_metadata.assert_called_once_with(video_url)

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_video_metadata_no_video_found(mock_youtube_service):
    mock_youtube_service.get_video_metadata.return_value = None

    video_url = "https://www.youtube.com/watch?v=non_existent_video_id"
    metadata = get_video_metadata(video_url)
    assert metadata is None

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_video_metadata_api_error(mock_youtube_service):
    mock_youtube_service.get_video_metadata.side_effect = Exception("API Error")

    video_url = "https://www.youtube.com/watch?v=error_video_id"
    metadata = get_video_metadata(video_url)
    assert metadata is None

@patch('casablanca.transcript_utils.youtube_service', spec=YouTubeService)
def test_get_video_metadata_invalid_url(mock_youtube_service):
    mock_youtube_service.get_video_metadata.return_value = None

    video_url = "invalid_url"
    metadata = get_video_metadata(video_url)
    assert metadata is None
    mock_youtube_service.get_video_metadata.assert_called_once_with(video_url)