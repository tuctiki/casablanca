import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from casablanca.main import cli, VideoMetadataError, TranscriptError
from datetime import datetime
from casablanca.config import OBSIDIAN_VAULT_PATH
import logging

# Helper function to run the main script with arguments and capture logs
def run_main(args, caplog, log_level=logging.INFO):
    runner = CliRunner()
    with caplog.at_level(log_level):
        result = runner.invoke(cli, args)
    return result.exit_code, caplog.text

# Fixture for common mock return values
@pytest.fixture
def mock_video_metadata():
    return {
        "title": "Test Video Title",
        "description": "Test Description",
        "publishedAt": "2023-10-26T12:00:00Z"
    }

# Test cases for conditional logic
@patch('casablanca.main.VideoProcessor._classify_video')
@patch('casablanca.main.VideoProcessor._get_video_info')
@patch('casablanca.main.YouTubeService')
@patch('casablanca.main.GeminiService')
def test_cli_non_finance_video(mock_gemini_service, mock_youtube_service, mock_get_video_info, mock_classify_video, mock_video_metadata, caplog):
    mock_get_video_info.return_value = MagicMock(
        title=mock_video_metadata['title'],
        description=mock_video_metadata['description'],
        published_at=datetime.strptime(mock_video_metadata['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
    )
    mock_classify_video.return_value = "Education"

    video_url = "https://www.youtube.com/watch?v=test_id"
    exit_code, logs = run_main([video_url], caplog)

    assert exit_code == 0
    assert "Video is not finance-related (Education). Skipping transcript fetching and summarization." in logs
    mock_classify_video.assert_called_once()
    mock_youtube_service.return_value.get_transcript.assert_not_called()
    mock_gemini_service.return_value.summarize_content.assert_not_called()