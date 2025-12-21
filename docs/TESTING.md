# Testing

## Run All Tests

```bash
pytest
```

## Run Tests with Coverage

```bash
pytest --cov=text2speech --cov-report=term --cov-report=html
```

## Run Specific Test Classes

```bash
# Test initialization
pytest tests/test_text2speech.py::TestText2SpeechInitialization

# Test audio queue
pytest tests/test_audio_queue.py::TestAudioQueueManager

# Test configuration
pytest tests/test_config.py::TestConfigDefaults
```

## Test Coverage

The test suite includes:
- ✅ Initialization tests
- ✅ Asynchronous operation tests
- ✅ Audio queue management tests
- ✅ Configuration system tests
- ✅ Audio generation and playback tests
- ✅ Command-line interface tests
- ✅ Error handling tests
- ✅ Edge case tests
- ✅ Integration tests
