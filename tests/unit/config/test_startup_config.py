"""Tests for StartUpConfig class.

This module tests:
- StartUpConfig field getters and setters
- Bit manipulation for mbist_dis, rngtest_dis, maintenance_ena
- to_dict() method
- String representation
- Inheritance from BaseConfig
"""

import pytest
from tropicsquare.config.startup import StartUpConfig
from tropicsquare.config.constants import (
    STARTUP_MBIST_DIS_BIT,
    STARTUP_RNGTEST_DIS_BIT,
    STARTUP_MAINTENANCE_ENA_BIT
)


class TestStartUpConfigInitialization:
    """Test StartUpConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization has all flags disabled (0xFFFFFFFF)."""
        config = StartUpConfig()
        # Default value 0xFFFFFFFF has all bits set
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = StartUpConfig(0x00000000)
        assert config._value == 0x00000000


class TestStartUpConfigFields:
    """Test StartUpConfig field properties."""

    def test_mbist_dis_getter_false(self):
        """Test mbist_dis getter when bit is 0."""
        config = StartUpConfig(0x00000000)
        assert config.mbist_dis is False

    def test_mbist_dis_getter_true(self):
        """Test mbist_dis getter when bit is 1."""
        value = 1 << STARTUP_MBIST_DIS_BIT
        config = StartUpConfig(value)
        assert config.mbist_dis is True

    def test_mbist_dis_setter_true(self):
        """Test mbist_dis setter sets bit correctly."""
        config = StartUpConfig(0x00000000)
        config.mbist_dis = True
        assert config._value == (1 << STARTUP_MBIST_DIS_BIT)
        assert config.mbist_dis is True

    def test_mbist_dis_setter_false(self):
        """Test mbist_dis setter clears bit correctly."""
        config = StartUpConfig(0xFFFFFFFF)
        config.mbist_dis = False
        assert config._value == (0xFFFFFFFF & ~(1 << STARTUP_MBIST_DIS_BIT))
        assert config.mbist_dis is False

    def test_rngtest_dis_getter_false(self):
        """Test rngtest_dis getter when bit is 0."""
        config = StartUpConfig(0x00000000)
        assert config.rngtest_dis is False

    def test_rngtest_dis_getter_true(self):
        """Test rngtest_dis getter when bit is 1."""
        value = 1 << STARTUP_RNGTEST_DIS_BIT
        config = StartUpConfig(value)
        assert config.rngtest_dis is True

    def test_rngtest_dis_setter_true(self):
        """Test rngtest_dis setter sets bit correctly."""
        config = StartUpConfig(0x00000000)
        config.rngtest_dis = True
        assert config._value == (1 << STARTUP_RNGTEST_DIS_BIT)
        assert config.rngtest_dis is True

    def test_rngtest_dis_setter_false(self):
        """Test rngtest_dis setter clears bit correctly."""
        config = StartUpConfig(0xFFFFFFFF)
        config.rngtest_dis = False
        assert config._value == (0xFFFFFFFF & ~(1 << STARTUP_RNGTEST_DIS_BIT))
        assert config.rngtest_dis is False

    def test_maintenance_ena_getter_false(self):
        """Test maintenance_ena getter when bit is 0."""
        config = StartUpConfig(0x00000000)
        assert config.maintenance_ena is False

    def test_maintenance_ena_getter_true(self):
        """Test maintenance_ena getter when bit is 1."""
        value = 1 << STARTUP_MAINTENANCE_ENA_BIT
        config = StartUpConfig(value)
        assert config.maintenance_ena is True

    def test_maintenance_ena_setter_true(self):
        """Test maintenance_ena setter sets bit correctly."""
        config = StartUpConfig(0x00000000)
        config.maintenance_ena = True
        assert config._value == (1 << STARTUP_MAINTENANCE_ENA_BIT)
        assert config.maintenance_ena is True

    def test_maintenance_ena_setter_false(self):
        """Test maintenance_ena setter clears bit correctly."""
        config = StartUpConfig(0xFFFFFFFF)
        config.maintenance_ena = False
        assert config._value == (0xFFFFFFFF & ~(1 << STARTUP_MAINTENANCE_ENA_BIT))
        assert config.maintenance_ena is False


class TestStartUpConfigMultipleFields:
    """Test setting multiple fields together."""

    def test_set_multiple_fields(self):
        """Test setting multiple fields at once."""
        config = StartUpConfig(0x00000000)

        config.mbist_dis = True
        config.rngtest_dis = True
        config.maintenance_ena = False

        assert config.mbist_dis is True
        assert config.rngtest_dis is True
        assert config.maintenance_ena is False

    def test_fields_dont_interfere(self):
        """Test that setting one field doesn't affect others."""
        config = StartUpConfig(0x00000000)

        # Set mbist_dis
        config.mbist_dis = True
        assert config.mbist_dis is True
        assert config.rngtest_dis is False
        assert config.maintenance_ena is False

        # Set rngtest_dis
        config.rngtest_dis = True
        assert config.mbist_dis is True
        assert config.rngtest_dis is True
        assert config.maintenance_ena is False


class TestStartUpConfigToDict:
    """Test to_dict() method."""

    def test_to_dict_all_false(self):
        """Test to_dict with all fields false."""
        config = StartUpConfig(0x00000000)
        result = config.to_dict()

        assert result == {
            'mbist_dis': False,
            'rngtest_dis': False,
            'maintenance_ena': False
        }

    def test_to_dict_all_true(self):
        """Test to_dict with all fields true."""
        config = StartUpConfig(0xFFFFFFFF)
        result = config.to_dict()

        assert result == {
            'mbist_dis': True,
            'rngtest_dis': True,
            'maintenance_ena': True
        }

    def test_to_dict_mixed(self):
        """Test to_dict with mixed field values."""
        config = StartUpConfig(0x00000000)
        config.mbist_dis = True
        config.maintenance_ena = True

        result = config.to_dict()

        assert result == {
            'mbist_dis': True,
            'rngtest_dis': False,
            'maintenance_ena': True
        }


class TestStartUpConfigStringRepresentation:
    """Test string representation."""

    def test_str_all_false(self):
        """Test __str__ with all fields false."""
        config = StartUpConfig(0x00000000)
        result = str(config)

        assert 'StartUpConfig' in result
        assert 'mbist_dis=False' in result
        assert 'rngtest_dis=False' in result
        assert 'maintenance_ena=False' in result

    def test_str_all_true(self):
        """Test __str__ with all fields true."""
        config = StartUpConfig(0xFFFFFFFF)
        result = str(config)

        assert 'StartUpConfig' in result
        assert 'mbist_dis=True' in result
        assert 'rngtest_dis=True' in result
        assert 'maintenance_ena=True' in result

    def test_str_mixed(self):
        """Test __str__ with mixed values."""
        config = StartUpConfig(0x00000000)
        config.rngtest_dis = True

        result = str(config)

        assert 'mbist_dis=False' in result
        assert 'rngtest_dis=True' in result
        assert 'maintenance_ena=False' in result


class TestStartUpConfigRoundTrip:
    """Test round-trip conversion."""

    def test_round_trip_via_bytes(self):
        """Test that from_bytes -> to_bytes preserves configuration."""
        # Create config with specific values
        original = StartUpConfig(0x00000000)
        original.mbist_dis = True
        original.maintenance_ena = True

        # Convert to bytes and back
        data = original.to_bytes()
        restored = StartUpConfig.from_bytes(data)

        # Verify all fields match
        assert restored.mbist_dis == original.mbist_dis
        assert restored.rngtest_dis == original.rngtest_dis
        assert restored.maintenance_ena == original.maintenance_ena


class TestStartUpConfigInheritance:
    """Test inheritance from BaseConfig."""

    def test_inherits_from_base_config(self):
        """Test that StartUpConfig inherits from BaseConfig."""
        from tropicsquare.config.base import BaseConfig

        config = StartUpConfig()
        assert isinstance(config, BaseConfig)

    def test_from_bytes_inherited(self):
        """Test that from_bytes works (inherited from BaseConfig)."""
        data = b'\x0E\x00\x00\x00'  # Some specific value
        config = StartUpConfig.from_bytes(data)

        assert config._value == 0x0000000E

    def test_to_bytes_inherited(self):
        """Test that to_bytes works (inherited from BaseConfig)."""
        config = StartUpConfig(0x12345678)
        data = config.to_bytes()

        assert data == b'\x78\x56\x34\x12'
        assert len(data) == 4
