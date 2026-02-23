"""Tests for SensorsConfig class.

This module tests:
- SensorsConfig field getters and setters
- Bit manipulation for 18 sensor disable flags
- Helper methods (_get_bit, _set_bit)
- to_dict() method
- String representation
- Inheritance from BaseConfig

Note: Tests sample of fields (first, middle, last) rather than all 18
to avoid excessive duplication while maintaining full coverage.
"""

import pytest
from tropicsquare.config.sensors import SensorsConfig
from tropicsquare.config.constants import (
    SENSORS_PTRNG0_TEST_DIS_BIT,
    SENSORS_PTRNG1_TEST_DIS_BIT,
    SENSORS_TEMP_DIS_BIT,
    SENSORS_BF_PLATFORM_DIS_BIT
)


class TestSensorsConfigInitialization:
    """Test SensorsConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        config = SensorsConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = SensorsConfig(0x00000000)
        assert config._value == 0x00000000


class TestSensorsConfigHelperMethods:
    """Test helper methods _get_bit and _set_bit."""

    def test_get_bit_returns_false_when_bit_is_zero(self):
        """Test _get_bit returns False when bit is 0."""
        config = SensorsConfig(0x00000000)
        assert config._get_bit(0) is False
        assert config._get_bit(5) is False
        assert config._get_bit(17) is False

    def test_get_bit_returns_true_when_bit_is_one(self):
        """Test _get_bit returns True when bit is 1."""
        config = SensorsConfig(0xFFFFFFFF)
        assert config._get_bit(0) is True
        assert config._get_bit(5) is True
        assert config._get_bit(17) is True

    def test_set_bit_true_sets_bit_to_one(self):
        """Test _set_bit(True) sets bit to 1."""
        config = SensorsConfig(0x00000000)
        config._set_bit(0, True)
        assert config._value == 0x00000001
        config._set_bit(5, True)
        assert config._value == 0x00000021

    def test_set_bit_false_clears_bit_to_zero(self):
        """Test _set_bit(False) clears bit to 0."""
        config = SensorsConfig(0xFFFFFFFF)
        config._set_bit(0, False)
        assert config._value == 0xFFFFFFFE
        config._set_bit(5, False)
        assert config._value == 0xFFFFFFDE


class TestSensorsConfigFirstField:
    """Test first field (ptrng0_test_dis)."""

    def test_ptrng0_test_dis_getter_false(self):
        """Test ptrng0_test_dis getter when bit is 0."""
        config = SensorsConfig(0x00000000)
        assert config.ptrng0_test_dis is False

    def test_ptrng0_test_dis_getter_true(self):
        """Test ptrng0_test_dis getter when bit is 1."""
        value = 1 << SENSORS_PTRNG0_TEST_DIS_BIT
        config = SensorsConfig(value)
        assert config.ptrng0_test_dis is True

    def test_ptrng0_test_dis_setter_true(self):
        """Test ptrng0_test_dis setter sets bit correctly."""
        config = SensorsConfig(0x00000000)
        config.ptrng0_test_dis = True
        assert config._value == (1 << SENSORS_PTRNG0_TEST_DIS_BIT)
        assert config.ptrng0_test_dis is True

    def test_ptrng0_test_dis_setter_false(self):
        """Test ptrng0_test_dis setter clears bit correctly."""
        config = SensorsConfig(0xFFFFFFFF)
        config.ptrng0_test_dis = False
        assert config._value == (0xFFFFFFFF & ~(1 << SENSORS_PTRNG0_TEST_DIS_BIT))
        assert config.ptrng0_test_dis is False


class TestSensorsConfigMiddleField:
    """Test middle field (temp_dis)."""

    def test_temp_dis_getter_false(self):
        """Test temp_dis getter when bit is 0."""
        config = SensorsConfig(0x00000000)
        assert config.temp_dis is False

    def test_temp_dis_getter_true(self):
        """Test temp_dis getter when bit is 1."""
        value = 1 << SENSORS_TEMP_DIS_BIT
        config = SensorsConfig(value)
        assert config.temp_dis is True

    def test_temp_dis_setter_true(self):
        """Test temp_dis setter sets bit correctly."""
        config = SensorsConfig(0x00000000)
        config.temp_dis = True
        assert config._value == (1 << SENSORS_TEMP_DIS_BIT)
        assert config.temp_dis is True

    def test_temp_dis_setter_false(self):
        """Test temp_dis setter clears bit correctly."""
        config = SensorsConfig(0xFFFFFFFF)
        config.temp_dis = False
        assert config._value == (0xFFFFFFFF & ~(1 << SENSORS_TEMP_DIS_BIT))
        assert config.temp_dis is False


class TestSensorsConfigLastField:
    """Test last field (bf_platform_dis)."""

    def test_bf_platform_dis_getter_false(self):
        """Test bf_platform_dis getter when bit is 0."""
        config = SensorsConfig(0x00000000)
        assert config.bf_platform_dis is False

    def test_bf_platform_dis_getter_true(self):
        """Test bf_platform_dis getter when bit is 1."""
        value = 1 << SENSORS_BF_PLATFORM_DIS_BIT
        config = SensorsConfig(value)
        assert config.bf_platform_dis is True

    def test_bf_platform_dis_setter_true(self):
        """Test bf_platform_dis setter sets bit correctly."""
        config = SensorsConfig(0x00000000)
        config.bf_platform_dis = True
        assert config._value == (1 << SENSORS_BF_PLATFORM_DIS_BIT)
        assert config.bf_platform_dis is True

    def test_bf_platform_dis_setter_false(self):
        """Test bf_platform_dis setter clears bit correctly."""
        config = SensorsConfig(0xFFFFFFFF)
        config.bf_platform_dis = False
        assert config._value == (0xFFFFFFFF & ~(1 << SENSORS_BF_PLATFORM_DIS_BIT))
        assert config.bf_platform_dis is False


class TestSensorsConfigMultipleFields:
    """Test setting multiple fields together."""

    def test_set_multiple_fields(self):
        """Test setting multiple fields at once."""
        config = SensorsConfig(0x00000000)

        config.ptrng0_test_dis = True
        config.ptrng1_test_dis = True
        config.temp_dis = True

        assert config.ptrng0_test_dis is True
        assert config.ptrng1_test_dis is True
        assert config.temp_dis is True

    def test_fields_dont_interfere(self):
        """Test that setting one field doesn't affect others."""
        config = SensorsConfig(0x00000000)

        # Set first field
        config.ptrng0_test_dis = True
        assert config.ptrng0_test_dis is True
        assert config.temp_dis is False
        assert config.bf_platform_dis is False

        # Set another field
        config.temp_dis = True
        assert config.ptrng0_test_dis is True
        assert config.temp_dis is True
        assert config.bf_platform_dis is False


class TestSensorsConfigToDict:
    """Test to_dict() method."""

    def test_to_dict_all_false(self):
        """Test to_dict with all fields false."""
        config = SensorsConfig(0x00000000)
        result = config.to_dict()

        # Check structure (should have all 18 fields)
        assert len(result) == 18
        assert all(value is False for value in result.values())

    def test_to_dict_all_true(self):
        """Test to_dict with all fields true."""
        config = SensorsConfig(0xFFFFFFFF)
        result = config.to_dict()

        # Check that all fields are True
        assert len(result) == 18
        # Note: Only first 18 bits should be checked (sensor fields)
        sensor_fields = [
            'ptrng0_test_dis', 'ptrng1_test_dis', 'oscmon_dis', 'shield_dis',
            'vmon_dis', 'glitch_dis', 'temp_dis', 'laser_dis', 'emp_dis',
            'cpu_alert_dis', 'bf_pin_ver_dis', 'bf_scb_dis', 'bf_cpb_dis',
            'bf_ecc_dis', 'bf_ram_dis', 'bf_ekdb_dis', 'bf_imem_dis',
            'bf_platform_dis'
        ]
        for field in sensor_fields:
            assert result[field] is True

    def test_to_dict_mixed(self):
        """Test to_dict with mixed field values."""
        config = SensorsConfig(0x00000000)
        config.ptrng0_test_dis = True
        config.temp_dis = True
        config.bf_platform_dis = True

        result = config.to_dict()

        assert result['ptrng0_test_dis'] is True
        assert result['temp_dis'] is True
        assert result['bf_platform_dis'] is True
        assert result['ptrng1_test_dis'] is False


class TestSensorsConfigStringRepresentation:
    """Test string representation."""

    def test_str_all_enabled(self):
        """Test __str__ with all sensors enabled (all bits 0)."""
        config = SensorsConfig(0x00000000)
        result = str(config)

        assert 'SensorsConfig' in result
        assert '18 enabled' in result
        assert '0 disabled' in result

    def test_str_all_disabled(self):
        """Test __str__ with all sensors disabled (all bits 1)."""
        config = SensorsConfig(0xFFFFFFFF)
        result = str(config)

        assert 'SensorsConfig' in result
        assert '0 enabled' in result
        assert '18 disabled' in result

    def test_str_mixed(self):
        """Test __str__ with mixed values."""
        config = SensorsConfig(0x00000000)
        # Disable 3 sensors
        config.ptrng0_test_dis = True
        config.temp_dis = True
        config.bf_platform_dis = True

        result = str(config)

        assert 'SensorsConfig' in result
        assert '15 enabled' in result
        assert '3 disabled' in result


class TestSensorsConfigRoundTrip:
    """Test round-trip conversion."""

    def test_round_trip_via_bytes(self):
        """Test that from_bytes -> to_bytes preserves configuration."""
        original = SensorsConfig(0x00000000)
        original.ptrng0_test_dis = True
        original.temp_dis = True
        original.bf_platform_dis = True

        data = original.to_bytes()
        restored = SensorsConfig.from_bytes(data)

        assert restored.ptrng0_test_dis == original.ptrng0_test_dis
        assert restored.temp_dis == original.temp_dis
        assert restored.bf_platform_dis == original.bf_platform_dis


class TestSensorsConfigInheritance:
    """Test inheritance from BaseConfig."""

    def test_inherits_from_base_config(self):
        """Test that SensorsConfig inherits from BaseConfig."""
        from tropicsquare.config.base import BaseConfig

        config = SensorsConfig()
        assert isinstance(config, BaseConfig)

    def test_from_bytes_inherited(self):
        """Test that from_bytes works (inherited from BaseConfig)."""
        data = b'\x0E\x00\x00\x00'
        config = SensorsConfig.from_bytes(data)
        assert config._value == 0x0000000E

    def test_to_bytes_inherited(self):
        """Test that to_bytes works (inherited from BaseConfig)."""
        config = SensorsConfig(0x12345678)
        data = config.to_bytes()
        assert data == b'\x78\x56\x34\x12'
        assert len(data) == 4
