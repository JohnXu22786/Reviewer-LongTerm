"""
Configuration management system - supports environment variables, config files, and parameter passing.
"""
import os
from pathlib import Path
from typing import Optional, Any
import yaml
from dataclasses import dataclass

from .default_config import default_config


@dataclass
class PluginConfig:
    """Plugin configuration."""
    data_dir: str
    debug_mode: bool
    default_review_limit: int
    base_intervals: list[int]
    initial_ef: float
    min_ef: float
    ef_penalty: float
    mastery_threshold: int

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'PluginConfig':
        """Create config from dictionary."""
        return cls(
            data_dir=config_dict.get('data_dir', default_config.DATA_DIR),
            debug_mode=config_dict.get('debug_mode', default_config.DEBUG_MODE),
            default_review_limit=config_dict.get('default_review_limit', default_config.DEFAULT_REVIEW_LIMIT),
            base_intervals=config_dict.get('base_intervals', list(default_config.BASE_INTERVALS)),
            initial_ef=config_dict.get('initial_ef', default_config.INITIAL_EF),
            min_ef=config_dict.get('min_ef', default_config.MIN_EF),
            ef_penalty=config_dict.get('ef_penalty', default_config.EF_PENALTY),
            mastery_threshold=config_dict.get('mastery_threshold', default_config.MASTERY_THRESHOLD)
        )


def get_config(data_dir: Optional[str] = None) -> PluginConfig:
    """
    Get configuration (supports parameter overrides).

    Priority order:
    1. Function parameter (data_dir)
    2. Environment variable (LEARNING_REVIEWER_DATA_DIR)
    3. Config file (config/learning_reviewer_config.yaml)
    4. Default values

    Args:
        data_dir: Optional data directory override

    Returns:
        PluginConfig instance
    """
    # 1. From environment variables
    env_data_dir = os.getenv("LEARNING_REVIEWER_DATA_DIR")
    env_debug_mode = os.getenv("LEARNING_REVIEWER_DEBUG", "").lower() in ("true", "1", "yes")

    # 2. From config file
    config_file_path = Path(__file__).parent.parent.parent.parent / "config" / "learning_reviewer_config.yaml"
    file_config = {}

    if config_file_path.exists():
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                file_data = yaml.safe_load(f)
                if file_data and 'learning_reviewer' in file_data:
                    file_config = file_data['learning_reviewer']
        except Exception as e:
            print(f"Warning: Failed to load config file {config_file_path}: {e}")

    # 3. Merge configuration
    # Determine data_dir (parameter > env > file > default)
    final_data_dir = (
        data_dir or
        env_data_dir or
        file_config.get('data_dir') or
        default_config.DATA_DIR
    )

    # Ensure data_dir is absolute and expanded
    final_data_dir = str(Path(final_data_dir).expanduser().resolve())

    # Build config dictionary
    config_dict = {
        'data_dir': final_data_dir,
        'debug_mode': env_debug_mode or file_config.get('debug_mode', default_config.DEBUG_MODE),
        'default_review_limit': file_config.get('default_review_limit', default_config.DEFAULT_REVIEW_LIMIT),
        'base_intervals': file_config.get('base_intervals', list(default_config.BASE_INTERVALS)),
        'initial_ef': file_config.get('initial_ef', default_config.INITIAL_EF),
        'min_ef': file_config.get('min_ef', default_config.MIN_EF),
        'ef_penalty': file_config.get('ef_penalty', default_config.EF_PENALTY),
        'mastery_threshold': file_config.get('mastery_threshold', default_config.MASTERY_THRESHOLD)
    }

    return PluginConfig.from_dict(config_dict)


def create_sample_config() -> dict:
    """Create sample configuration for documentation."""
    return {
        'learning_reviewer': {
            'data_dir': './data',
            'debug_mode': False,
            'default_review_limit': 20,
            'base_intervals': [1, 1, 3, 7, 15, 30],
            'initial_ef': 2.5,
            'min_ef': 1.3,
            'ef_penalty': 0.2,
            'mastery_threshold': 7
        }
    }