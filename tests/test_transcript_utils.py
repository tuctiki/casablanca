import pytest
from unittest.mock import patch
from casablanca.transcript_utils import get_transcript
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled

@patch('casablanca.transcript_utils.YouTubeTranscriptApi')
def test_get_transcript_success(mock_youtube_transcript_api):
    # Mock the fetch method to return a sample transcript
    mock_instance = mock_youtube_transcript_api.return_value
    mock_instance.fetch.return_value = [
        {'text': 'Hello', 'start': 0.0, 'duration': 1.0},
        {'text': 'World', 'start': 1.0, 'duration': 1.0}
    ]

    video_url = "https://www.youtube.com/watch?v=test_video_id"
    transcript = get_transcript(video_url)

    assert transcript == "Hello\nWorld"
    mock_instance.fetch.assert_called_once_with("test_video_id")

@patch('casablanca.transcript_utils.YouTubeTranscriptApi')
def test_get_transcript_no_transcript_found(mock_youtube_transcript_api):
    mock_instance = mock_youtube_transcript_api.return_value
    mock_instance.fetch.side_effect = NoTranscriptFound

    video_url = "https://www.youtube.com/watch?v=no_transcript_id"
    transcript = get_transcript(video_url)

    assert transcript is None

@patch('casablanca.transcript_utils.YouTubeTranscriptApi')
def test_get_transcript_transcripts_disabled(mock_youtube_transcript_api):
    mock_instance = mock_youtube_transcript_api.return_value
    mock_instance.fetch.side_effect = TranscriptsDisabled

    video_url = "https://www.youtube.com/watch?v=disabled_transcript_id"
    transcript = get_transcript(video_url)

    assert transcript is None

@patch('casablanca.transcript_utils.YouTubeTranscriptApi')
def test_get_transcript_invalid_url(mock_youtube_transcript_api):
    video_url = "invalid_url"
    transcript = get_transcript(video_url)

    assert transcript is None
    mock_youtube_transcript_api.return_value.fetch.assert_not_called()