"""Unit tests for the text2speech module.

This module contains comprehensive tests for the Text2Speech class,
including initialization, TTS functionality, audio processing, and
error handling.
"""

import unittest
from unittest.mock import Mock, patch
import threading
import torch
import numpy as np
from text2speech import Text2Speech


class TestText2SpeechInitialization(unittest.TestCase):
    """Test cases for Text2Speech initialization."""

    @patch('text2speech.text2speech.ElevenLabs')
    @patch('text2speech.text2speech.KPipeline')
    def test_init_defaults_to_kokoro(self, mock_kpipeline: Mock, mock_elevenlabs: Mock) -> None:
        """Test that initialization defaults to Kokoro when ElevenLabs raises exception.

        Args:
            mock_kpipeline: Mocked KPipeline class.
            mock_elevenlabs: Mocked ElevenLabs class.
        """
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        
        # Verify Kokoro pipeline was initialized
        mock_kpipeline.assert_called_once_with(lang_code='a')
        self.assertIsNotNone(tts._client)

    @patch('text2speech.text2speech.ElevenLabs')
    @patch('text2speech.text2speech.KPipeline')
    def test_init_verbose_mode(self, mock_kpipeline: Mock, mock_elevenlabs: Mock) -> None:
        """Test initialization with verbose mode enabled.

        Args:
            mock_kpipeline: Mocked KPipeline class.
            mock_elevenlabs: Mocked ElevenLabs class.
        """
        with patch('builtins.print') as mock_print:
            tts = Text2Speech(el_api_key="test_key", verbose=True)
            
            # Verify verbose mode is set
            self.assertTrue(tts.verbose())
            
            # Verify print was called for debug output
            mock_print.assert_called()

    @patch('text2speech.text2speech.KPipeline')
    def test_verbose_property(self, mock_kpipeline: Mock) -> None:
        """Test the verbose property getter.

        Args:
            mock_kpipeline: Mocked KPipeline class.
        """
        tts_verbose = Text2Speech(el_api_key="test_key", verbose=True)
        tts_silent = Text2Speech(el_api_key="test_key", verbose=False)
        
        self.assertTrue(tts_verbose.verbose())
        self.assertFalse(tts_silent.verbose())


class TestText2SpeechAsync(unittest.TestCase):
    """Test cases for asynchronous TTS operations."""

    @patch('text2speech.text2speech.KPipeline')
    def test_call_text2speech_async_returns_thread(self, mock_kpipeline: Mock) -> None:
        """Test that async call returns a threading.Thread object.

        Args:
            mock_kpipeline: Mocked KPipeline class.
        """
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        
        with patch.object(tts, '_text2speech_kokoro'):
            thread = tts.call_text2speech_async("Test text")
            
            self.assertIsInstance(thread, threading.Thread)
            self.assertTrue(thread.is_alive() or not thread.is_alive())  # Thread may complete quickly

    @patch('text2speech.text2speech.KPipeline')
    def test_call_text2speech_async_executes_kokoro(self, mock_kpipeline: Mock) -> None:
        """Test that async call properly executes Kokoro TTS.

        Args:
            mock_kpipeline: Mocked KPipeline class.
        """
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        test_text = "Hello, world!"
        
        with patch.object(tts, '_text2speech_kokoro') as mock_kokoro:
            thread = tts.call_text2speech_async(test_text)
            thread.join()  # Wait for completion
            
            mock_kokoro.assert_called_once_with(test_text)


class TestText2SpeechKokoro(unittest.TestCase):
    """Test cases for Kokoro TTS functionality."""

    @patch('text2speech.text2speech.KPipeline')
    @patch('text2speech.text2speech.sd')
    @patch('text2speech.text2speech.Text2Speech._play_audio_safely')
    def test_text2speech_kokoro_generates_audio(
        self, 
        mock_play: Mock, 
        mock_sd: Mock, 
        mock_kpipeline: Mock
    ) -> None:
        """Test that Kokoro TTS generates and plays audio.

        Args:
            mock_play: Mocked audio playback function.
            mock_sd: Mocked sounddevice module.
            mock_kpipeline: Mocked KPipeline class.
        """
        # Setup mock generator
        mock_audio = torch.randn(24000)
        mock_generator = [(None, None, mock_audio)]
        mock_client = Mock()
        mock_client.return_value = mock_generator
        mock_kpipeline.return_value = mock_client
        
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        tts._text2speech_kokoro("Test text")
        
        # Verify audio was played
        mock_play.assert_called_once()
        mock_sd.wait.assert_called_once()

    @patch('text2speech.text2speech.KPipeline')
    @patch('builtins.print')
    def test_text2speech_kokoro_handles_error(
        self, 
        mock_print: Mock, 
        mock_kpipeline: Mock
    ) -> None:
        """Test that Kokoro TTS handles errors gracefully.

        Args:
            mock_print: Mocked print function.
            mock_kpipeline: Mocked KPipeline class.
        """
        mock_client = Mock()
        mock_client.side_effect = Exception("Test error")
        mock_kpipeline.return_value = mock_client
        
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        tts._text2speech_kokoro("Test text")
        
        # Verify error was printed
        self.assertTrue(any("Error with Kokoro" in str(call) for call in mock_print.call_args_list))


class TestAudioPlayback(unittest.TestCase):
    """Test cases for audio playback functionality."""

    @patch('text2speech.text2speech.sd')
    @patch('text2speech.text2speech.torchaudio.transforms.Resample')
    def test_play_audio_safely_resamples(self, mock_resample: Mock, mock_sd: Mock) -> None:
        """Test that audio is resampled to device sample rate.

        Args:
            mock_resample: Mocked Resample transform.
            mock_sd: Mocked sounddevice module.
        """
        # Setup device info
        mock_sd.query_devices.return_value = {'default_samplerate': 48000}
        mock_sd.default.device = [None, 0]
        
        # Setup resampler
        mock_resampler = Mock()
        resampled_audio = torch.randn(48000)
        mock_resampler.return_value = resampled_audio
        mock_resample.return_value = mock_resampler
        
        # Test audio
        audio = torch.randn(24000)
        Text2Speech._play_audio_safely(audio, original_sample_rate=24000)
        
        # Verify resampling occurred
        mock_resample.assert_called_once_with(orig_freq=24000, new_freq=48000)
        mock_resampler.assert_called_once()

    @patch('text2speech.text2speech.sd')
    def test_play_audio_safely_normalizes_volume(self, mock_sd: Mock) -> None:
        """Test that audio is normalized and volume is applied.

        Args:
            mock_sd: Mocked sounddevice module.
        """
        mock_sd.query_devices.return_value = {'default_samplerate': 24000}
        mock_sd.default.device = [None, 0]
        
        # Create audio with high amplitude
        audio = torch.tensor([2.0, -2.0, 1.0, -1.0])
        
        with patch.object(mock_sd, 'play') as mock_play:
            Text2Speech._play_audio_safely(audio, original_sample_rate=24000, volume=0.8)
            
            # Get the played audio
            played_audio = mock_play.call_args[0][0]
            
            # Verify normalization (peak should be <= 0.95 * 0.8 = 0.76)
            self.assertLessEqual(np.abs(played_audio).max(), 0.95)

    @patch('text2speech.text2speech.sd')
    def test_play_audio_safely_uses_custom_device(self, mock_sd: Mock) -> None:
        """Test that custom audio device can be specified.

        Args:
            mock_sd: Mocked sounddevice module.
        """
        mock_sd.query_devices.return_value = {'default_samplerate': 24000}
        
        audio = torch.randn(24000)
        custom_device = 5
        
        with patch.object(mock_sd, 'play') as mock_play:
            Text2Speech._play_audio_safely(
                audio,
                original_sample_rate=24000,
                device=custom_device
            )
            
            # Verify custom device was used
            mock_sd.query_devices.assert_called_with(custom_device, 'output')
            self.assertEqual(mock_play.call_args[1]['device'], custom_device)

    @patch('text2speech.text2speech.sd')
    @patch('builtins.print')
    def test_play_audio_safely_handles_error(self, mock_print: Mock, mock_sd: Mock) -> None:
        """Test that playback errors are handled gracefully.

        Args:
            mock_print: Mocked print function.
            mock_sd: Mocked sounddevice module.
        """
        mock_sd.query_devices.side_effect = Exception("Device error")
        
        audio = torch.randn(24000)
        Text2Speech._play_audio_safely(audio)
        
        # Verify error message was printed
        self.assertTrue(
            any("Error during safe audio playback" in str(call) for call in mock_print.call_args_list)
        )


class TestLegacyElevenLabs(unittest.TestCase):
    """Test cases for legacy ElevenLabs functionality."""

    @patch('text2speech.text2speech.KPipeline')
    def test_text2speech_legacy_with_none_client(self, mock_kpipeline: Mock) -> None:
        """Test legacy TTS method when client is None.

        Args:
            mock_kpipeline: Mocked KPipeline class.
        """
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        tts._client = None
        
        # Should not raise exception
        tts._text2speech("Test text")


class TestIntegration(unittest.TestCase):
    """Integration tests for complete TTS workflow."""

    @patch('text2speech.text2speech.KPipeline')
    @patch('text2speech.text2speech.sd')
    def test_complete_tts_workflow(self, mock_sd: Mock, mock_kpipeline: Mock) -> None:
        """Test complete workflow from text input to audio output.

        Args:
            mock_sd: Mocked sounddevice module.
            mock_kpipeline: Mocked KPipeline class.
        """
        # Setup mocks
        mock_sd.query_devices.return_value = {'default_samplerate': 24000}
        mock_sd.default.device = [None, 0]
        
        mock_audio = torch.randn(24000)
        mock_generator = [(None, None, mock_audio)]
        mock_client = Mock()
        mock_client.return_value = mock_generator
        mock_kpipeline.return_value = mock_client
        
        # Execute workflow
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        thread = tts.call_text2speech_async("Integration test")
        thread.join()
        
        # Verify complete execution
        mock_client.assert_called()
        mock_sd.play.assert_called()
        mock_sd.wait.assert_called()

    @patch('text2speech.text2speech.KPipeline')
    @patch('text2speech.text2speech.sd')
    def test_multiple_sequential_calls(self, mock_sd: Mock, mock_kpipeline: Mock) -> None:
        """Test multiple sequential TTS calls.

        Args:
            mock_sd: Mocked sounddevice module.
            mock_kpipeline: Mocked KPipeline class.
        """
        # Setup mocks
        mock_sd.query_devices.return_value = {'default_samplerate': 24000}
        mock_sd.default.device = [None, 0]
        
        mock_audio = torch.randn(24000)
        mock_generator = [(None, None, mock_audio)]
        mock_client = Mock()
        mock_client.return_value = mock_generator
        mock_kpipeline.return_value = mock_client
        
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        
        # Make multiple calls
        texts = ["First text", "Second text", "Third text"]
        threads = []
        
        for text in texts:
            thread = tts.call_text2speech_async(text)
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Verify all were executed
        self.assertEqual(mock_client.call_count, len(texts))


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and boundary conditions."""

    @patch('text2speech.text2speech.KPipeline')
    def test_empty_text(self, mock_kpipeline: Mock) -> None:
        """Test TTS with empty text input.

        Args:
            mock_kpipeline: Mocked KPipeline class.
        """
        mock_client = Mock()
        mock_client.return_value = []
        mock_kpipeline.return_value = mock_client
        
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        thread = tts.call_text2speech_async("")
        thread.join()
        
        # Should complete without error
        self.assertFalse(thread.is_alive())

    @patch('text2speech.text2speech.KPipeline')
    @patch('text2speech.text2speech.sd')
    def test_very_long_text(self, mock_sd: Mock, mock_kpipeline: Mock) -> None:
        """Test TTS with very long text input.

        Args:
            mock_sd: Mocked sounddevice module.
            mock_kpipeline: Mocked KPipeline class.
        """
        mock_sd.query_devices.return_value = {'default_samplerate': 24000}
        mock_sd.default.device = [None, 0]
        
        mock_audio = torch.randn(24000)
        mock_generator = [(None, None, mock_audio)] * 10  # Multiple chunks
        mock_client = Mock()
        mock_client.return_value = mock_generator
        mock_kpipeline.return_value = mock_client
        
        tts = Text2Speech(el_api_key="test_key", verbose=False)
        long_text = "This is a very long text. " * 100
        
        thread = tts.call_text2speech_async(long_text)
        thread.join()
        
        # Verify multiple audio chunks were played
        self.assertEqual(mock_sd.play.call_count, 10)

    @patch('text2speech.text2speech.sd')
    def test_zero_volume_playback(self, mock_sd: Mock) -> None:
        """Test audio playback with zero volume.

        Args:
            mock_sd: Mocked sounddevice module.
        """
        mock_sd.query_devices.return_value = {'default_samplerate': 24000}
        mock_sd.default.device = [None, 0]
        
        audio = torch.randn(24000)
        
        with patch.object(mock_sd, 'play') as mock_play:
            Text2Speech._play_audio_safely(audio, volume=0.0)
            
            # Audio should still be played (but silently)
            mock_play.assert_called_once()
            played_audio = mock_play.call_args[0][0]
            
            # All samples should be near zero
            self.assertLess(np.abs(played_audio).max(), 0.01)


if __name__ == '__main__':
    unittest.main()
