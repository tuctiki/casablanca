import pytest
from unittest.mock import patch
from casablanca.llm_utils import summarize_content
import os

@patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'})
@patch('google.generativeai.GenerativeModel')
def test_summarize_content_success(mock_generative_model):
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.return_value.text = "This is a summary."

    text = "Some long text to summarize."
    prompt = "Summarize this text."
    summary = summarize_content(text, prompt)

    assert summary == "This is a summary."
    mock_generative_model.assert_called_once_with('gemini-2.5-flash')
    mock_model_instance.generate_content.assert_called_once()

@patch.dict(os.environ, {}, clear=True)
def test_summarize_content_no_api_key():
    text = "Some text."
    prompt = "Summarize."
    summary = summarize_content(text, prompt)

    assert summary == "Error: Could not generate summary."

@patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'})
@patch('google.generativeai.GenerativeModel')
def test_summarize_content_api_failure(mock_generative_model):
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.side_effect = Exception("API error")

    text = "Some text."
    prompt = "Summarize."
    summary = summarize_content(text, prompt)

    assert summary == "Error: Could not generate summary."