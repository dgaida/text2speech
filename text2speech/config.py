"""Configuration management for text2speech module.

This module provides utilities for loading and managing configuration
from YAML files with proper defaults and validation.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, List
import yaml

from .constants import (
    DEFAULT_VOLUME,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_SPEED,
)


class Config:
    """Configuration manager for text2speech settings."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "audio": {
            "output_device": None,
            "default_volume": DEFAULT_VOLUME,
            "sample_rate": DEFAULT_SAMPLE_RATE,
        },
        "tts": {
            "engine": "kokoro",
            "kokoro": {
                "lang_code": "a",
                "voice": "af_heart",
                "speed": DEFAULT_SPEED,
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

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize configuration.

        Args:
            config_path: Path to config.yaml file. If None, searches in common locations.
        """
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()

        if config_path is None:
            config_path = self._find_config_file()

        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)

    def _find_config_file(self) -> Optional[str]:
        """Search for config.yaml in common locations.

        Returns:
            Path to config file if found, None otherwise.
        """
        search_paths: List[str] = [
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
                user_config: Dict[str, Any] = yaml.safe_load(f) or {}

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
        result: Dict[str, Any] = base.copy()

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
        keys: List[str] = key_path.split(".")
        value: Any = self._config

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
        keys: List[str] = key_path.split(".")
        config: Dict[str, Any] = self._config

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

        Raises:
            ValueError: If path is outside allowed directories.
        """
        path = Path(config_path).resolve()

        # Restrict to safe directories
        allowed_prefixes = [
            Path.home().resolve(),
            Path.cwd().resolve(),
            Path(tempfile.gettempdir()).resolve(),
        ]

        is_allowed = False
        for prefix in allowed_prefixes:
            try:
                path.relative_to(prefix)
                is_allowed = True
                break
            except ValueError:
                continue

        if not is_allowed:
            raise ValueError(f"Config path outside allowed directories: {config_path}")

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    @property
    def audio_output_device(self) -> Optional[int]:
        """Get audio output device ID."""
        val = self.get("audio.output_device")
        return int(val) if val is not None else None

    @property
    def audio_volume(self) -> float:
        """Get default audio volume."""
        return float(self.get("audio.default_volume", DEFAULT_VOLUME))

    @property
    def sample_rate(self) -> int:
        """Get sample rate."""
        return int(self.get("audio.sample_rate", DEFAULT_SAMPLE_RATE))

    @property
    def tts_engine(self) -> str:
        """Get TTS engine name."""
        return str(self.get("tts.engine", "kokoro"))

    @property
    def kokoro_lang_code(self) -> str:
        """Get Kokoro language code."""
        return str(self.get("tts.kokoro.lang_code", "a"))

    @property
    def kokoro_voice(self) -> str:
        """Get Kokoro voice."""
        return str(self.get("tts.kokoro.voice", "af_heart"))

    @property
    def kokoro_speed(self) -> float:
        """Get Kokoro speech speed."""
        return float(self.get("tts.kokoro.speed", DEFAULT_SPEED))

    @property
    def kokoro_split_pattern(self) -> str:
        """Get Kokoro text split pattern."""
        return str(self.get("tts.kokoro.split_pattern", r"\n+"))

    @property
    def verbose(self) -> bool:
        """Get verbose logging setting."""
        return bool(self.get("logging.verbose", False))

    @property
    def use_gpu(self) -> bool:
        """Get GPU usage setting."""
        return bool(self.get("performance.use_gpu", True))
