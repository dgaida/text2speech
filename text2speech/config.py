"""Configuration management for text2speech module.

This module provides utilities for loading and managing configuration
from YAML files with proper defaults and validation.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class Config:
    """Configuration manager for text2speech settings."""

    DEFAULT_CONFIG = {
        "audio": {
            "output_device": None,
            "default_volume": 0.8,
            "sample_rate": 24000,
        },
        "tts": {
            "engine": "kokoro",
            "kokoro": {
                "lang_code": "a",
                "voice": "af_heart",
                "speed": 1.0,
                "split_pattern": r"\n+",
            },
            "elevenlabs": {
                "voice": "Brian",
                "model": "eleven_multilingual_v2",
            },
        },
        "logging": {
            "verbose": False,
            "log_file": None,
            "log_level": "INFO",
        },
        "performance": {
            "use_gpu": True,
            "num_threads": 1,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config.yaml file. If None, searches in common locations.
        """
        self._config = self.DEFAULT_CONFIG.copy()

        if config_path is None:
            config_path = self._find_config_file()

        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)

    def _find_config_file(self) -> Optional[str]:
        """Search for config.yaml in common locations.

        Returns:
            Path to config file if found, None otherwise.
        """
        search_paths = [
            "config.yaml",
            "config.yml",
            os.path.expanduser("~/.text2speech/config.yaml"),
            os.path.expanduser("~/.config/text2speech/config.yaml"),
            "/etc/text2speech/config.yaml",
        ]

        for path in search_paths:
            if os.path.exists(path):
                return path

        return None

    def load_from_file(self, config_path: str) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Path to the YAML configuration file.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            yaml.YAMLError: If config file is invalid YAML.
        """
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}

            # Deep merge user config with defaults
            self._config = self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)

        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file: {e}")

    @staticmethod
    def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.

        Args:
            base: Base dictionary.
            update: Dictionary with updates to apply.

        Returns:
            Merged dictionary.
        """
        result = base.copy()

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value (e.g., 'audio.output_device').
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        keys = key_path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value (e.g., 'audio.output_device').
            value: Value to set.
        """
        keys = key_path.split(".")
        config = self._config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary.

        Returns:
            Complete configuration dictionary.
        """
        return self._config.copy()

    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to YAML file.

        Args:
            config_path: Path where to save the configuration.
        """
        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    @property
    def audio_output_device(self) -> Optional[int]:
        """Get audio output device ID."""
        return self.get("audio.output_device")

    @property
    def audio_volume(self) -> float:
        """Get default audio volume."""
        return self.get("audio.default_volume", 0.8)

    @property
    def sample_rate(self) -> int:
        """Get sample rate."""
        return self.get("audio.sample_rate", 24000)

    @property
    def tts_engine(self) -> str:
        """Get TTS engine name."""
        return self.get("tts.engine", "kokoro")

    @property
    def kokoro_lang_code(self) -> str:
        """Get Kokoro language code."""
        return self.get("tts.kokoro.lang_code", "a")

    @property
    def kokoro_voice(self) -> str:
        """Get Kokoro voice."""
        return self.get("tts.kokoro.voice", "af_heart")

    @property
    def kokoro_speed(self) -> float:
        """Get Kokoro speech speed."""
        return self.get("tts.kokoro.speed", 1.0)

    @property
    def kokoro_split_pattern(self) -> str:
        """Get Kokoro text split pattern."""
        return self.get("tts.kokoro.split_pattern", r"\n+")

    @property
    def verbose(self) -> bool:
        """Get verbose logging setting."""
        return self.get("logging.verbose", False)

    @property
    def use_gpu(self) -> bool:
        """Get GPU usage setting."""
        return self.get("performance.use_gpu", True)
