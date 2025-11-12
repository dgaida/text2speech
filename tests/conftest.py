"""Pytest configuration and fixtures for text2speech tests.

This module provides shared fixtures and configuration for the test suite.
"""

import pytest
from unittest.mock import Mock, patch
import torch


@pytest.fixture
def mock_kokoro_pipeline():
    """Provide a mocked KPipeline for testing.

    Yields:
        Mock: A mocked KPipeline instance.
    """
    with patch("text2speech.text2speech.KPipeline") as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def mock_sounddevice():
    """Provide a mocked sounddevice module for testing.

    Yields:
        Mock: A mocked sounddevice module.
    """
    with patch("text2speech.text2speech.sd") as mock:
        mock.query_devices.return_value = {"default_samplerate": 24000}
        mock.default.device = [None, 0]
        yield mock


@pytest.fixture
def sample_audio_tensor():
    """Provide a sample audio tensor for testing.

    Returns:
        torch.Tensor: A 1-second audio tensor at 24kHz sample rate.
    """
    return torch.randn(24000)


@pytest.fixture
def sample_texts():
    """Provide sample texts for testing.

    Returns:
        list[str]: A list of sample text strings.
    """
    return [
        "Hello, this is a test.",
        "This is another test sentence.",
        "Short text.",
        "A much longer text that contains multiple clauses and should be handled properly by the system.",
    ]
