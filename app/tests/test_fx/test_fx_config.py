"""
Test configuration for FX tests.
This module provides test utilities and fixtures for FX-related tests.
"""

import tempfile
from pathlib import Path


class FXTestConfig:
    """Configuration class for FX tests."""

    @staticmethod
    def create_temp_directories():
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        data_dir = Path(temp_dir) / "data" / "fx"
        web_data_dir = Path(temp_dir) / "web" / "_data"

        data_dir.mkdir(parents=True, exist_ok=True)
        web_data_dir.mkdir(parents=True, exist_ok=True)

        return temp_dir, data_dir, web_data_dir

    @staticmethod
    def sample_fx_rates():
        """Return sample FX rates for testing."""
        return {
            "USD": {"buy": 17.50, "sell": 17.55, "mid": 17.525},
            "GBP": {"buy": 22.10, "sell": 22.15, "mid": 22.125},
            "EUR": {"buy": 19.80, "sell": 19.85, "mid": 19.825},
            "ZAR": {"buy": 0.95, "sell": 0.98, "mid": 0.965},
        }
