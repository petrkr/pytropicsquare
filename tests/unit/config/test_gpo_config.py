"""Tests for GpoConfig class.

This module tests:
- GpoConfig field getter and setter
- Integer field manipulation for gpo_func (0-7)
- Range validation
- to_dict() method
- String representation
- Inheritance from BaseConfig
"""

import pytest
from tropicsquare.config.gpo import GpoConfig
from tropicsquare.config.constants import GPO_FUNC_MASK, GPO_FUNC_POS


class TestGpoConfigInitialization:
    """Test GpoConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        config = GpoConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = GpoConfig(0x00000000)
        assert config._value == 0x00000000


class TestGpoConfigField:
    """Test GpoConfig field property."""

    def test_gpo_func_getter_zero(self):
        """Test gpo_func getter when value is 0."""
        config = GpoConfig(0x00000000)
        assert config.gpo_func == 0

    def test_gpo_func_getter_max(self):
        """Test gpo_func getter when value is 7 (max)."""
        config = GpoConfig(0x00000007)
        assert config.gpo_func == 7

    def test_gpo_func_getter_mid_value(self):
        """Test gpo_func getter with mid-range value."""
        config = GpoConfig(0x00000004)
        assert config.gpo_func == 4

    def test_gpo_func_getter_extracts_only_3_bits(self):
        """Test that gpo_func getter extracts only 3 bits."""
        # Set value with other bits set
        config = GpoConfig(0xFFFFFFF5)  # ...11110101
        assert config.gpo_func == 5  # Only bits 2-0

    def test_gpo_func_setter_zero(self):
        """Test gpo_func setter sets value to 0."""
        config = GpoConfig(0xFFFFFFFF)
        config.gpo_func = 0
        assert config.gpo_func == 0

    def test_gpo_func_setter_max(self):
        """Test gpo_func setter sets value to 7 (max)."""
        config = GpoConfig(0x00000000)
        config.gpo_func = 7
        assert config.gpo_func == 7

    def test_gpo_func_setter_mid_value(self):
        """Test gpo_func setter with mid-range value."""
        config = GpoConfig(0x00000000)
        config.gpo_func = 3
        assert config.gpo_func == 3

    def test_gpo_func_setter_preserves_other_bits(self):
        """Test that gpo_func setter preserves other bits."""
        config = GpoConfig(0xFFFFFFF8)  # ...11111000
        config.gpo_func = 2  # Set to ...00010
        assert config._value == 0xFFFFFFFA  # Should be ...11111010

    def test_gpo_func_setter_clears_previous_value(self):
        """Test that gpo_func setter clears previous value in field."""
        config = GpoConfig(0x00000007)  # gpo_func = 7
        config.gpo_func = 1  # Change to 1
        assert config.gpo_func == 1
        assert config._value == 0x00000001


class TestGpoConfigValidation:
    """Test GpoConfig range validation."""

    def test_gpo_func_setter_rejects_negative(self):
        """Test that gpo_func setter rejects negative values."""
        config = GpoConfig()
        with pytest.raises(ValueError) as exc_info:
            config.gpo_func = -1
        assert "gpo_func must be 0-7" in str(exc_info.value)

    def test_gpo_func_setter_rejects_too_large(self):
        """Test that gpo_func setter rejects values > 7."""
        config = GpoConfig()
        with pytest.raises(ValueError) as exc_info:
            config.gpo_func = 8
        assert "gpo_func must be 0-7" in str(exc_info.value)

    def test_gpo_func_setter_accepts_all_valid_values(self):
        """Test that gpo_func setter accepts all valid values 0-7."""
        config = GpoConfig()
        for value in range(8):
            config.gpo_func = value
            assert config.gpo_func == value


class TestGpoConfigToDict:
    """Test to_dict() method."""

    def test_to_dict_zero(self):
        """Test to_dict when gpo_func is 0."""
        config = GpoConfig(0x00000000)
        result = config.to_dict()
        assert result == {'gpo_func': 0}

    def test_to_dict_max(self):
        """Test to_dict when gpo_func is 7."""
        config = GpoConfig(0x00000007)
        result = config.to_dict()
        assert result == {'gpo_func': 7}

    def test_to_dict_mid(self):
        """Test to_dict with mid-range value."""
        config = GpoConfig(0x00000004)
        result = config.to_dict()
        assert result == {'gpo_func': 4}


class TestGpoConfigStringRepresentation:
    """Test string representation."""

    def test_str_zero(self):
        """Test __str__ when gpo_func is 0."""
        config = GpoConfig(0x00000000)
        result = str(config)
        assert 'GpoConfig' in result
        assert 'gpo_func=0' in result

    def test_str_max(self):
        """Test __str__ when gpo_func is 7."""
        config = GpoConfig(0x00000007)
        result = str(config)
        assert 'GpoConfig' in result
        assert 'gpo_func=7' in result

    def test_str_mid(self):
        """Test __str__ with mid-range value."""
        config = GpoConfig(0x00000003)
        result = str(config)
        assert 'GpoConfig' in result
        assert 'gpo_func=3' in result


class TestGpoConfigRoundTrip:
    """Test round-trip conversion."""

    def test_round_trip_via_bytes(self):
        """Test that from_bytes -> to_bytes preserves configuration."""
        original = GpoConfig(0x00000000)
        original.gpo_func = 5

        data = original.to_bytes()
        restored = GpoConfig.from_bytes(data)

        assert restored.gpo_func == original.gpo_func


class TestGpoConfigInheritance:
    """Test inheritance from BaseConfig."""

    def test_inherits_from_base_config(self):
        """Test that GpoConfig inherits from BaseConfig."""
        from tropicsquare.config.base import BaseConfig

        config = GpoConfig()
        assert isinstance(config, BaseConfig)

    def test_from_bytes_inherited(self):
        """Test that from_bytes works (inherited from BaseConfig)."""
        data = b'\x00\x00\x00\x03'
        config = GpoConfig.from_bytes(data)
        assert config._value == 0x00000003
        assert config.gpo_func == 3

    def test_to_bytes_inherited(self):
        """Test that to_bytes works (inherited from BaseConfig)."""
        config = GpoConfig(0x00000006)
        data = config.to_bytes()
        assert data == b'\x00\x00\x00\x06'
        assert len(data) == 4
