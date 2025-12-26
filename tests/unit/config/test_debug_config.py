"""Tests for DebugConfig class.

This module tests:
- DebugConfig field getter and setter
- Bit manipulation for fw_log_en
- to_dict() method
- String representation
- Inheritance from BaseConfig
"""

import pytest
from tropicsquare.config.debug import DebugConfig
from tropicsquare.config.constants import DEBUG_FW_LOG_EN_BIT


class TestDebugConfigInitialization:
    """Test DebugConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        config = DebugConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = DebugConfig(0x00000000)
        assert config._value == 0x00000000


class TestDebugConfigField:
    """Test DebugConfig field property."""

    def test_fw_log_en_getter_false(self):
        """Test fw_log_en getter when bit is 0."""
        config = DebugConfig(0x00000000)
        assert config.fw_log_en is False

    def test_fw_log_en_getter_true(self):
        """Test fw_log_en getter when bit is 1."""
        value = 1 << DEBUG_FW_LOG_EN_BIT
        config = DebugConfig(value)
        assert config.fw_log_en is True

    def test_fw_log_en_setter_true(self):
        """Test fw_log_en setter sets bit correctly."""
        config = DebugConfig(0x00000000)
        config.fw_log_en = True
        assert config._value == (1 << DEBUG_FW_LOG_EN_BIT)
        assert config.fw_log_en is True

    def test_fw_log_en_setter_false(self):
        """Test fw_log_en setter clears bit correctly."""
        config = DebugConfig(0xFFFFFFFF)
        config.fw_log_en = False
        assert config._value == (0xFFFFFFFF & ~(1 << DEBUG_FW_LOG_EN_BIT))
        assert config.fw_log_en is False


class TestDebugConfigToDict:
    """Test to_dict() method."""

    def test_to_dict_false(self):
        """Test to_dict when field is false."""
        config = DebugConfig(0x00000000)
        result = config.to_dict()
        assert result == {'fw_log_en': False}

    def test_to_dict_true(self):
        """Test to_dict when field is true."""
        config = DebugConfig(0xFFFFFFFF)
        result = config.to_dict()
        assert result == {'fw_log_en': True}


class TestDebugConfigStringRepresentation:
    """Test string representation."""

    def test_str_false(self):
        """Test __str__ when field is false."""
        config = DebugConfig(0x00000000)
        result = str(config)
        assert 'DebugConfig' in result
        assert 'fw_log_en=False' in result

    def test_str_true(self):
        """Test __str__ when field is true."""
        config = DebugConfig(0xFFFFFFFF)
        result = str(config)
        assert 'DebugConfig' in result
        assert 'fw_log_en=True' in result


class TestDebugConfigRoundTrip:
    """Test round-trip conversion."""

    def test_round_trip_via_bytes(self):
        """Test that from_bytes -> to_bytes preserves configuration."""
        original = DebugConfig(0x00000000)
        original.fw_log_en = True

        data = original.to_bytes()
        restored = DebugConfig.from_bytes(data)

        assert restored.fw_log_en == original.fw_log_en


class TestDebugConfigInheritance:
    """Test inheritance from BaseConfig."""

    def test_inherits_from_base_config(self):
        """Test that DebugConfig inherits from BaseConfig."""
        from tropicsquare.config.base import BaseConfig

        config = DebugConfig()
        assert isinstance(config, BaseConfig)

    def test_from_bytes_inherited(self):
        """Test that from_bytes works (inherited from BaseConfig)."""
        data = b'\x00\x00\x00\x01'
        config = DebugConfig.from_bytes(data)
        assert config._value == 0x00000001

    def test_to_bytes_inherited(self):
        """Test that to_bytes works (inherited from BaseConfig)."""
        config = DebugConfig(0x00000001)
        data = config.to_bytes()
        assert data == b'\x00\x00\x00\x01'
        assert len(data) == 4
