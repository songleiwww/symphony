"""
Tests for Weather API client
"""
import pytest


def test_import():
    """Test that we can import the main module"""
    try:
        import weather_tool
        assert True
    except ImportError:
        assert False, "Failed to import weather_tool"


def test_config_import():
    """Test that we can import the config module"""
    try:
        import config
        assert True
    except ImportError:
        assert False, "Failed to import config"
