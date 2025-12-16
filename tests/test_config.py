"""Unit tests for the configuration module."""

import unittest
import tempfile
import os
import yaml
from text2speech.config import Config


class TestConfigDefaults(unittest.TestCase):
    """Test cases for default configuration values."""

    def test_default_audio_settings(self):
        """Test that default audio settings are correct."""
        config = Config()

        self.assertIsNone(config.audio_output_device)
        self.assertEqual(config.audio_volume, 0.8)
        self.assertEqual(config.sample_rate, 24000)

    def test_default_tts_settings(self):
        """Test that default TTS settings are correct."""
        config = Config()

        self.assertEqual(config.tts_engine, "kokoro")
        self.assertEqual(config.kokoro_lang_code, "a")
        self.assertEqual(config.kokoro_voice, "af_heart")
        self.assertEqual(config.kokoro_speed, 1.0)
        self.assertEqual(config.kokoro_split_pattern, r"\n+")

    def test_default_logging_settings(self):
        """Test that default logging settings are correct."""
        config = Config()

        self.assertFalse(config.verbose)
        self.assertEqual(config.get("logging.log_level"), "INFO")
        self.assertIsNone(config.get("logging.log_file"))

    def test_default_performance_settings(self):
        """Test that default performance settings are correct."""
        config = Config()

        self.assertTrue(config.use_gpu)
        self.assertEqual(config.get("performance.num_threads"), 1)


class TestConfigFileLoading(unittest.TestCase):
    """Test cases for loading configuration from files."""

    def setUp(self):
        """Create a temporary config file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yaml")

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        # Only remove directory if it's empty
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            # Directory not empty, clean up remaining files
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_custom_audio_device(self):
        """Test loading custom audio device from config file."""
        config_data = {"audio": {"output_device": 4}}

        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f)

        config = Config(self.config_path)
        self.assertEqual(config.audio_output_device, 4)

    def test_load_custom_voice_settings(self):
        """Test loading custom voice settings from config file."""
        config_data = {"tts": {"kokoro": {"voice": "am_adam", "speed": 1.2, "lang_code": "b"}}}

        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f)

        config = Config(self.config_path)
        self.assertEqual(config.kokoro_voice, "am_adam")
        self.assertEqual(config.kokoro_speed, 1.2)
        self.assertEqual(config.kokoro_lang_code, "b")

    def test_partial_config_override(self):
        """Test that partial config overrides work correctly."""
        config_data = {"audio": {"default_volume": 0.5}}

        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f)

        config = Config(self.config_path)

        # Overridden value
        self.assertEqual(config.audio_volume, 0.5)

        # Default values still present
        self.assertIsNone(config.audio_output_device)
        self.assertEqual(config.sample_rate, 24000)

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        # Config.__init__ doesn't raise error if path doesn't exist when config_path is provided
        # It only raises if load_from_file is called explicitly
        with self.assertRaises(FileNotFoundError):
            config = Config()
            config.load_from_file("/nonexistent/path/config.yaml")

    def test_load_invalid_yaml_raises_error(self):
        """Test that loading invalid YAML raises YAMLError."""
        with open(self.config_path, "w") as f:
            f.write("invalid: yaml: content: {\n")

        with self.assertRaises(yaml.YAMLError):
            Config(self.config_path)


class TestConfigGetSet(unittest.TestCase):
    """Test cases for getting and setting configuration values."""

    def setUp(self):
        """Initialize a config instance for testing."""
        self.config = Config()

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        value = self.config.get("audio.output_device")
        self.assertIsNone(value)

        value = self.config.get("tts.kokoro.voice")
        self.assertEqual(value, "af_heart")

    def test_get_nonexistent_value_returns_default(self):
        """Test that getting non-existent values returns default."""
        value = self.config.get("nonexistent.key", "default")
        self.assertEqual(value, "default")

    def test_set_nested_value(self):
        """Test setting nested configuration values."""
        self.config.set("audio.output_device", 5)
        self.assertEqual(self.config.audio_output_device, 5)

        self.config.set("tts.kokoro.speed", 1.5)
        self.assertEqual(self.config.kokoro_speed, 1.5)

    def test_set_creates_nested_structure(self):
        """Test that setting creates nested dictionaries as needed."""
        self.config.set("new.nested.key", "value")
        self.assertEqual(self.config.get("new.nested.key"), "value")


class TestConfigSave(unittest.TestCase):
    """Test cases for saving configuration to file."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "saved_config.yaml")

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        # Clean up any subdirectories created
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_to_file(self):
        """Test saving configuration to file."""
        config = Config()
        config.set("audio.output_device", 7)
        config.set("tts.kokoro.voice", "bf_emma")

        config.save_to_file(self.config_path)

        # Verify file exists
        self.assertTrue(os.path.exists(self.config_path))

        # Load saved config and verify values
        loaded_config = Config(self.config_path)
        self.assertEqual(loaded_config.audio_output_device, 7)
        self.assertEqual(loaded_config.kokoro_voice, "bf_emma")

    def test_save_creates_directory(self):
        """Test that save creates parent directories if needed."""
        nested_path = os.path.join(self.temp_dir, "subdir", "config.yaml")

        config = Config()
        config.save_to_file(nested_path)

        self.assertTrue(os.path.exists(nested_path))


class TestConfigProperties(unittest.TestCase):
    """Test cases for configuration property accessors."""

    def test_all_properties_accessible(self):
        """Test that all property accessors work."""
        config = Config()

        # Audio properties
        _ = config.audio_output_device
        _ = config.audio_volume
        _ = config.sample_rate

        # TTS properties
        _ = config.tts_engine
        _ = config.kokoro_lang_code
        _ = config.kokoro_voice
        _ = config.kokoro_speed
        _ = config.kokoro_split_pattern

        # Logging properties
        _ = config.verbose

        # Performance properties
        _ = config.use_gpu


class TestConfigDeepMerge(unittest.TestCase):
    """Test cases for deep merge functionality."""

    def test_deep_merge_preserves_base(self):
        """Test that deep merge preserves base dictionary values."""
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        update = {"a": {"b": 10}}

        result = Config._deep_merge(base, update)

        self.assertEqual(result["a"]["b"], 10)  # Updated
        self.assertEqual(result["a"]["c"], 2)  # Preserved
        self.assertEqual(result["d"], 3)  # Preserved

    def test_deep_merge_adds_new_keys(self):
        """Test that deep merge adds new keys."""
        base = {"a": 1}
        update = {"b": 2, "c": {"d": 3}}

        result = Config._deep_merge(base, update)

        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"], 2)
        self.assertEqual(result["c"]["d"], 3)

    def test_deep_merge_overwrites_non_dict(self):
        """Test that deep merge overwrites non-dict values."""
        base = {"a": {"b": 1}}
        update = {"a": "string"}

        result = Config._deep_merge(base, update)

        self.assertEqual(result["a"], "string")


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for configuration system."""

    def test_complete_workflow(self):
        """Test complete configuration workflow."""
        # Create custom config
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "workflow_config.yaml")

        try:
            # Create and save initial config
            config1 = Config()
            config1.set("audio.output_device", 2)
            config1.set("tts.kokoro.voice", "am_adam")
            config1.save_to_file(config_path)

            # Load config in new instance
            config2 = Config(config_path)

            # Verify values transferred
            self.assertEqual(config2.audio_output_device, 2)
            self.assertEqual(config2.kokoro_voice, "am_adam")

            # Modify and save again
            config2.set("audio.default_volume", 0.6)
            config2.save_to_file(config_path)

            # Load final config
            config3 = Config(config_path)
            self.assertEqual(config3.audio_volume, 0.6)
            self.assertEqual(config3.audio_output_device, 2)

        finally:
            # Cleanup
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
