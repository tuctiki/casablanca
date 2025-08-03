import pytest
from unittest.mock import patch, MagicMock
from casablanca.processor import VideoProcessor
from casablanca.exceptions import VideoMetadataError, TranscriptError
from casablanca.models import Video
from datetime import datetime

@pytest.fixture
def mock_youtube_service():
    return MagicMock()

@pytest.fixture
def mock_gemini_service():
    return MagicMock()

@pytest.fixture
def mock_video():
    return Video(
        title="Test Video",
        description="Test Description",
        published_at=datetime(2023, 1, 1)
    )

@pytest.fixture
def processor(mock_youtube_service, mock_gemini_service):
    return VideoProcessor(mock_youtube_service, mock_gemini_service, "/fake/obsidian/path", ["Finance", "News"])

def test_get_video_info_success(processor, mock_youtube_service, mock_video):
    mock_youtube_service.get_video_metadata.return_value = mock_video
    video = processor._get_video_info("some_url")
    assert video == mock_video

def test_get_video_info_failure(processor, mock_youtube_service):
    mock_youtube_service.get_video_metadata.return_value = None
    with pytest.raises(VideoMetadataError):
        processor._get_video_info("some_url")

@patch('os.path.exists')
def test_check_existing_output_exists(mock_exists, processor, mock_video):
    mock_exists.return_value = True
    assert processor._check_existing_output("video_id", mock_video, False) is True

@patch('os.path.exists')
def test_check_existing_output_not_exists(mock_exists, processor, mock_video):
    mock_exists.return_value = False
    assert processor._check_existing_output("video_id", mock_video, False) is False

def test_classify_video(processor, mock_gemini_service):
    mock_gemini_service.get_video_category.return_value = "Finance"
    category = processor._classify_video("title", "description", "Finance,News")
    assert category == "Finance"

@patch('builtins.open')
@patch('casablanca.processor.move_to_obsidian')
def test_process_finance_video(mock_move, mock_open, processor, mock_youtube_service, mock_gemini_service, mock_video):
    mock_youtube_service.get_transcript.return_value = "transcript"
    mock_gemini_service.summarize_content.return_value = "summary"
    processor._process_finance_video("url", "dir", "exp_path", "mkt_path", "exp_prompt", "mkt_prompt", mock_video)
    assert mock_youtube_service.get_transcript.called
    assert mock_gemini_service.summarize_content.call_count == 2
    assert mock_move.called

def test_process_finance_video_no_transcript(processor, mock_youtube_service):
    mock_youtube_service.get_transcript.return_value = None
    with pytest.raises(TranscriptError):
        processor._process_finance_video("url", "dir", "exp_path", "mkt_path", "exp_prompt", "mkt_prompt", MagicMock())        

@patch('casablanca.processor.generate_output_paths')
@patch('os.makedirs')
def test_process_news_video(mock_mkdirs, mock_paths, processor, mock_youtube_service, mock_gemini_service, mock_video):
    mock_paths.return_value = ("dir", "exp_path", "mkt_path")
    processor._get_video_info = MagicMock(return_value=mock_video)
    processor._check_existing_output = MagicMock(return_value=False)
    processor._classify_video = MagicMock(return_value="News")
    processor._process_finance_video = MagicMock()

    processor.process("some_url", False, "exp_prompt", "mkt_prompt", "Finance,News")

    assert processor._process_finance_video.called

@patch('casablanca.processor.generate_output_paths')
@patch('os.makedirs')
def test_process_existing_output(mock_mkdirs, mock_paths, processor, mock_video):
    mock_paths.return_value = ("dir", "exp_path", "mkt_path")
    processor._get_video_info = MagicMock(return_value=mock_video)
    processor._check_existing_output = MagicMock(return_value=True)
    processor._classify_video = MagicMock()
    processor._process_finance_video = MagicMock()

    processor.process("some_url", False, "exp_prompt", "mkt_prompt", "Finance,News")

    assert not processor._classify_video.called
    assert not processor._process_finance_video.called
