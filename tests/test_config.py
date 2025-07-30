import pytest
import os
from unittest.mock import patch

# Temporarily modify sys.path to allow importing from src
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.casablanca.config import get_api_key

def test_get_api_key_raises_error_if_not_set():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="TEST_API_KEY environment variable not set."):
            get_api_key("TEST_API_KEY")
