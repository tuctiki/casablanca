import pytest
from unittest.mock import patch, MagicMock
from casablanca.llm_utils import summarize_content, get_video_category
from casablanca.services import GeminiService
from casablanca.config import GEMINI_API_KEY

@patch('casablanca.llm_utils.gemini_service', spec=GeminiService)
def test_summarize_content_success(mock_gemini_service):
    mock_gemini_service.summarize_content.return_value = "This is a summary."

    text = "Some long text to summarize."
    prompt = "Summarize this text."
    summary = summarize_content(text, prompt)

    assert summary == "This is a summary."
    mock_gemini_service.summarize_content.assert_called_once_with(text, prompt)

@patch('casablanca.llm_utils.gemini_service', spec=GeminiService)
def test_summarize_content_api_failure(mock_gemini_service):
    mock_gemini_service.summarize_content.side_effect = Exception("API error")

    text = "Some text."
    prompt = "Summarize."
    summary = summarize_content(text, prompt)

    assert summary == "Error: Could not generate summary."

@patch('casablanca.llm_utils.gemini_service', spec=GeminiService)
def test_get_video_category_success(mock_gemini_service):
    mock_gemini_service.get_video_category.return_value = "Finance"

    title = "Video Title"
    description = "Video Description"
    categories = ["Finance", "News"]
    category = get_video_category(title, description, categories)

    assert category == "Finance"
    mock_gemini_service.get_video_category.assert_called_once_with(title, description, categories)

@patch('casablanca.llm_utils.gemini_service', spec=GeminiService)
def test_get_video_category_api_failure(mock_gemini_service):
    mock_gemini_service.get_video_category.side_effect = Exception("API error")

    title = "Video Title"
    description = "Video Description"
    categories = ["Finance", "News"]
    category = get_video_category(title, description, categories)

    assert category == "Error"