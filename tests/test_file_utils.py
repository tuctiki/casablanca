import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from casablanca.file_utils import move_to_obsidian
from casablanca.models import Video
from datetime import datetime

@pytest.fixture
def setup_temp_files(tmp_path):
    expert_summary = tmp_path / "expert_summary.md"
    market_summary = tmp_path / "market_summary.md"
    expert_summary.write_text("Expert content")
    market_summary.write_text("Market content")
    return str(expert_summary), str(market_summary)

@patch('os.path.expanduser', side_effect=lambda path: path)
@patch('os.makedirs')
@patch('shutil.move')
@patch('logging.info')
def test_move_to_obsidian_success(mock_log_info, mock_shutil_move, mock_makedirs, mock_expanduser, setup_temp_files):
    expert_summary_path, market_summary_path = setup_temp_files
    video_title = "Test Video"
    video_date = "2023-01-01"
    obsidian_path = "/mock/obsidian/vault"

    video = Video(title=video_title, description="Test Description", published_at=datetime(2023, 1, 1))
    move_to_obsidian(video, expert_summary_path, market_summary_path, obsidian_path)

    mock_makedirs.assert_called_once()
    assert mock_shutil_move.call_count == 2
    mock_log_info.assert_called_with(f"Moved summary files to Obsidian vault: {os.path.join(obsidian_path, video_date, video_title)}")

@patch('os.path.expanduser', side_effect=lambda path: path)
@patch('os.makedirs')
@patch('shutil.move', side_effect=Exception("Permission denied"))
@patch('logging.warning')
@patch('logging.info')
@patch('logging.error')
def test_move_to_obsidian_error_handling(mock_log_error, mock_log_info, mock_log_warning, mock_shutil_move, mock_makedirs, mock_expanduser, setup_temp_files):
    expert_summary_path, market_summary_path = setup_temp_files
    video_title = "Test Video"
    video_date = "2023-01-01"
    obsidian_path = "/mock/obsidian/vault"

    video = Video(title=video_title, description="Test Description", published_at=datetime(2023, 1, 1))
    move_to_obsidian(video, expert_summary_path, market_summary_path, obsidian_path)

    mock_log_error.assert_called_once_with(f"Error moving summary files: Permission denied")

@patch('logging.warning')
def test_move_to_obsidian_no_obsidian_path(mock_log_warning):
    video_title = "Test Video"
    video_date = "2023-01-01"
    expert_summary_path = "/tmp/expert.md"
    market_summary_path = "/tmp/market.md"
    obsidian_path = None

    video = Video(title=video_title, description="Test Description", published_at=datetime(2023, 1, 1))
    move_to_obsidian(video, expert_summary_path, market_summary_path, obsidian_path)

    mock_log_warning.assert_called_once_with("OBSIDIAN_VAULT_PATH not set. Skipping move to Obsidian.")
