"""Tests for SleepModeConfig class.

This module tests:
- SleepModeConfig field getter and setter
- Bit manipulation for sleep_mode_en
- to_dict() method
- String representation
- Inheritance from BaseConfig
"""

import pytest
from tropicsquare.config.sleep_mode import SleepModeConfig
from tropicsquare.config.constants import SLEEP_MODE_EN_BIT


class TestSleepModeConfigInitialization:
    """Test SleepModeConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        config = SleepModeConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = SleepModeConfig(0x00000000)
        assert config._value == 0x00000000


class TestSleepModeConfigField:
    """Test SleepModeConfig field property."""

    def test_sleep_mode_en_getter_false(self):
        """Test sleep_mode_en getter when bit is 0."""
        config = SleepModeConfig(0x00000000)
        assert config.sleep_mode_en is False

    def test_sleep_mode_en_getter_true(self):
        """Test sleep_mode_en getter when bit is 1."""
        value = 1 << SLEEP_MODE_EN_BIT
        config = SleepModeConfig(value)
        assert config.sleep_mode_en is True

    def test_sleep_mode_en_setter_true(self):
        """Test sleep_mode_en setter sets bit correctly."""
        config = SleepModeConfig(0x00000000)
        config.sleep_mode_en = True
        assert config._value == (1 << SLEEP_MODE_EN_BIT)
        assert config.sleep_mode_en is True

    def test_sleep_mode_en_setter_false(self):
        """Test sleep_mode_en setter clears bit correctly."""
        config = SleepModeConfig(0xFFFFFFFF)
        config.sleep_mode_en = False
        assert config._value == (0xFFFFFFFF & ~(1 << SLEEP_MODE_EN_BIT))
        assert config.sleep_mode_en is False


class TestSleepModeConfigToDict:
    """Test to_dict() method."""

    def test_to_dict_false(self):
        """Test to_dict when field is false."""
        config = SleepModeConfig(0x00000000)
        result = config.to_dict()
        assert result == {'sleep_mode_en': False}

    def test_to_dict_true(self):
        """Test to_dict when field is true."""
        config = SleepModeConfig(0xFFFFFFFF)
        result = config.to_dict()
        assert result == {'sleep_mode_en': True}


class TestSleepModeConfigStringRepresentation:
    """Test string representation."""

    def test_str_false(self):
        """Test __str__ when field is false."""
        config = SleepModeConfig(0x00000000)
        result = str(config)
        assert 'SleepModeConfig' in result
        assert 'sleep_mode_en=False' in result

    def test_str_true(self):
        """Test __str__ when field is true."""
        config = SleepModeConfig(0xFFFFFFFF)
        result = str(config)
        assert 'SleepModeConfig' in result
        assert 'sleep_mode_en=True' in result


class TestSleepModeConfigRoundTrip:
    """Test round-trip conversion."""

    def test_round_trip_via_bytes(self):
        """Test that from_bytes -> to_bytes preserves configuration."""
        original = SleepModeConfig(0x00000000)
        original.sleep_mode_en = True

        data = original.to_bytes()
        restored = SleepModeConfig.from_bytes(data)

        assert restored.sleep_mode_en == original.sleep_mode_en


class TestSleepModeConfigInheritance:
    """Test inheritance from BaseConfig."""

    def test_inherits_from_base_config(self):
        """Test that SleepModeConfig inherits from BaseConfig."""
        from tropicsquare.config.base import BaseConfig

        config = SleepModeConfig()
        assert isinstance(config, BaseConfig)

    def test_from_bytes_inherited(self):
        """Test that from_bytes works (inherited from BaseConfig)."""
        data = b'\x01\x00\x00\x00'
        config = SleepModeConfig.from_bytes(data)
        assert config._value == 0x00000001

    def test_to_bytes_inherited(self):
        """Test that to_bytes works (inherited from BaseConfig)."""
        config = SleepModeConfig(0x00000001)
        data = config.to_bytes()
        assert data == b'\x01\x00\x00\x00'
        assert len(data) == 4
