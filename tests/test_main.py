import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from casablanca.main import cli
from datetime import datetime
from casablanca.config import OBSIDIAN_VAULT_PATH
import logging

# Helper function to run the main script with arguments
def run_main(args):
    runner = CliRunner()
    result = runner.invoke(cli, args)
    # Ensure logs are flushed before returning
    for handler in logging.root.handlers:
        handler.flush()
    return result.exit_code, result.stdout

@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript')
@patch('casablanca.main.summarize_content')
@patch('casablanca.main.get_video_category')
@patch('casablanca.main.move_to_obsidian')
def test_cache_skips_if_folder_exists(mock_move, mock_cat, mock_summary, mock_transcript, mock_get_video_metadata):
    # Arrange: Mock video metadata and create a fake Obsidian output folder
    video_url = "https://www.youtube.com/watch?v=2H4a12KB3jI"
    video_title = "Test Video Title"
    mock_get_video_metadata.return_value = {"title": video_title, "description": "Test Description", "publishedAt": "2023-10-26T12:00:00Z"}
    
    if OBSIDIAN_VAULT_PATH:
        obsidian_path = os.path.expanduser(OBSIDIAN_VAULT_PATH)
        date_folder = datetime.now().strftime("%Y-%m-%d")
        sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        obsidian_dest_folder = os.path.join(obsidian_path, date_folder, sanitized_title)
        os.makedirs(obsidian_dest_folder, exist_ok=True)

    # Act: Run the main script
    exit_code, stdout = run_main([video_url])

    # Assert: Check that the script logged a skipping message and exited
    assert exit_code == 0
    mock_transcript.assert_not_called()
    mock_summary.assert_not_called()
    mock_move.assert_not_called()
    mock_cat.assert_called_once()

    # Cleanup
    if OBSIDIAN_VAULT_PATH and os.path.exists(obsidian_dest_folder):
        shutil.rmtree(obsidian_dest_folder)

@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript', return_value="This is a test transcript.")
@patch('casablanca.main.summarize_content', return_value="This is a test summary.")
@patch('casablanca.main.get_video_category', return_value="Finance")
@patch('casablanca.main.move_to_obsidian', return_value=None)
def test_force_processes_if_folder_exists(mock_move, mock_cat, mock_summary, mock_transcript, mock_get_video_metadata):
    # Arrange: Mock video metadata and create a fake Obsidian output folder
    video_url = "https://www.youtube.com/watch?v=2H4a12KB3jI"
    video_title = "Test Video Title"
    mock_get_video_metadata.return_value = {"title": video_title, "description": "Test Description", "publishedAt": "2023-10-26T12:00:00Z"}
    
    if OBSIDIAN_VAULT_PATH:
        obsidian_path = os.path.expanduser(OBSIDIAN_VAULT_PATH)
        date_folder = datetime.now().strftime("%Y-%m-%d")
        sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        obsidian_dest_folder = os.path.join(obsidian_path, date_folder, sanitized_title)
        os.makedirs(obsidian_dest_folder, exist_ok=True)

    # Act: Run the main script with the --force flag
    exit_code, stdout = run_main([video_url, "--force"])

    # Assert: Check that the script did NOT log a skipping message
    assert exit_code == 0
    mock_transcript.assert_called_once()
    mock_summary.assert_called()
    mock_move.assert_called_once()
    mock_cat.assert_called_once()

    # Cleanup
    if OBSIDIAN_VAULT_PATH and os.path.exists(obsidian_dest_folder):
        shutil.rmtree(obsidian_dest_folder)

@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript')
@patch('casablanca.main.summarize_content')
@patch('casablanca.main.get_video_category')
@patch('casablanca.main.move_to_obsidian')
def test_custom_categories_option(mock_move, mock_cat, mock_summary, mock_transcript, mock_get_video_metadata):
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    video_title = "Test Video Title"
    video_description = "Test Description"
    mock_get_video_metadata.return_value = {"title": video_title, "description": video_description, "publishedAt": "2023-10-26T12:00:00Z"}
    mock_cat.return_value = "CustomCategory"

    custom_categories = "CustomCategory1,CustomCategory2"
    exit_code, stdout = run_main([video_url, "--categories", custom_categories])

    assert exit_code == 0
    mock_cat.assert_called_once_with(video_title, video_description, ["CustomCategory1", "CustomCategory2"])

@patch('casablanca.main.get_video_metadata', return_value=None)
def test_invalid_url_exits_with_error(mock_get_video_metadata):
    video_url = "invalid_url"
    exit_code, stdout = run_main([video_url])
    assert exit_code == 1
    mock_get_video_metadata.assert_called_once_with(video_url)
    assert "Failed to get video metadata. Exiting." in stdout

@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript', return_value=None)
@patch('casablanca.main.get_video_category', return_value="Finance")
def test_transcript_failure_exits_with_error(mock_get_video_category, mock_get_transcript, mock_get_video_metadata):
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    mock_get_video_metadata.return_value = {"title": "Test Title", "description": "Test Description", "publishedAt": "2023-10-26T12:00:00Z"}
    exit_code, stdout = run_main([video_url])
    assert exit_code == 1
    mock_get_transcript.assert_called_once_with(video_url)
    assert "Failed to fetch transcript. Exiting summarization process." in stdout

@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript')
@patch('casablanca.main.summarize_content')
@patch('casablanca.main.get_video_category', return_value="Sports")
@patch('casablanca.main.move_to_obsidian')
def test_non_finance_video_skips_summarization(mock_move, mock_cat, mock_summary, mock_transcript, mock_get_video_metadata):
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    mock_get_video_metadata.return_value = {"title": "Test Title", "description": "Test Description", "publishedAt": "2023-10-26T12:00:00Z"}
    exit_code, stdout = run_main([video_url])
    assert exit_code == 0
    mock_cat.assert_called_once()
    mock_transcript.assert_not_called()
    mock_summary.assert_not_called()
    mock_move.assert_not_called()
    assert "Video is not finance-related (Sports). Skipping transcript fetching and summarization." in stdout

@patch('casablanca.main.get_video_metadata', return_value=None)
def test_log_level_option(mock_get_video_metadata):
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    exit_code, stdout = run_main([video_url, "--log-level", "DEBUG"])
    assert exit_code == 1
    mock_get_video_metadata.assert_called_once_with(video_url)
    assert "Failed to get video metadata. Exiting." in stdout

@patch('casablanca.main.OBSIDIAN_VAULT_PATH', None)
@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript', return_value="This is a test transcript.")
@patch('casablanca.main.summarize_content', return_value="This is a test summary.")
@patch('casablanca.main.get_video_category', return_value="Finance")
def test_move_to_obsidian_logs_warning_if_path_not_set(mock_get_video_category, mock_summarize_content, mock_get_transcript, mock_get_video_metadata):
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    mock_get_video_metadata.return_value = {"title": "Test Title", "description": "Test Description", "publishedAt": "2023-10-26T12:00:00Z"}
    exit_code, stdout = run_main([video_url])
    assert exit_code == 0
    assert "OBSIDIAN_VAULT_PATH not set. Skipping move to Obsidian." in stdout