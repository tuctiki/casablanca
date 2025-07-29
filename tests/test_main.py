import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from casablanca import main

# Helper function to run the main script with arguments
def run_main(args):
    with patch('sys.argv', ['casablanca/main.py'] + args):
        with patch('casablanca.main.configure_logging'), patch('casablanca.main.clear_log_handlers'):
            return main.run_casablanca(args[0], force=('--force' in args))

@patch('casablanca.main.configure_logging')
@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript')
@patch('casablanca.main.summarize_content')
@patch('casablanca.main.get_video_category')
@patch('casablanca.main.move_to_obsidian')
def test_cache_skips_if_folder_exists(mock_move, mock_cat, mock_summary, mock_transcript, mock_get_video_metadata, mock_configure_logging, caplog):
    # Arrange: Mock video metadata and create a fake Obsidian output folder
    video_url = "https://www.youtube.com/watch?v=2H4a12KB3jI"
    video_title = "Test Video Title"
    mock_get_video_metadata.return_value = {"title": video_title, "description": "Test Description"}
    
    obsidian_path = os.path.expanduser("~/Documents/obsidian/casablanca")
    date_folder = main.datetime.now().strftime("%Y-%m-%d")
    sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    obsidian_dest_folder = os.path.join(obsidian_path, date_folder, sanitized_title)
    os.makedirs(obsidian_dest_folder, exist_ok=True)

    # Act: Run the main script
    exit_code = run_main([video_url])

    # Assert: Check that the script logged a skipping message and exited
    assert exit_code == 0
    mock_transcript.assert_not_called()
    mock_summary.assert_not_called()
    mock_move.assert_not_called()
    mock_cat.assert_not_called()

    # Cleanup
    shutil.rmtree(obsidian_dest_folder)

@patch('casablanca.main.configure_logging')
@patch('casablanca.main.get_video_metadata')
@patch('casablanca.main.get_transcript', return_value="This is a test transcript.")
@patch('casablanca.main.summarize_content', return_value="This is a test summary.")
@patch('casablanca.main.get_video_category', return_value="Finance")
@patch('casablanca.main.move_to_obsidian', return_value=None)
def test_force_processes_if_folder_exists(mock_move, mock_cat, mock_summary, mock_transcript, mock_get_video_metadata, mock_configure_logging, caplog):
    # Arrange: Mock video metadata and create a fake Obsidian output folder
    video_url = "https://www.youtube.com/watch?v=2H4a12KB3jI"
    video_title = "Test Video Title"
    mock_get_video_metadata.return_value = {"title": video_title, "description": "Test Description"}
    
    obsidian_path = os.path.expanduser("~/Documents/obsidian/casablanca")
    date_folder = main.datetime.now().strftime("%Y-%m-%d")
    sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    obsidian_dest_folder = os.path.join(obsidian_path, date_folder, sanitized_title)
    os.makedirs(obsidian_dest_folder, exist_ok=True)

    # Act: Run the main script with the --force flag
    exit_code = run_main([video_url, "--force"])

    # Assert: Check that the script did NOT log a skipping message
    assert exit_code == 0
    mock_transcript.assert_called_once()
    mock_summary.assert_called()
    mock_move.assert_called_once()
    mock_cat.assert_called_once()

    # Cleanup
    shutil.rmtree(obsidian_dest_folder)
