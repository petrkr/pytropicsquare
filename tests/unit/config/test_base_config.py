"""Tests for BaseConfig class.

This module tests:
- Configuration object initialization
- Byte conversion (from_bytes, to_bytes)
- Round-trip conversion
- String representations (__repr__, __str__)
- Default values and edge cases
"""

import pytest
from tropicsquare.config.base import BaseConfig


class TestBaseConfigInitialization:
    """Test BaseConfig initialization."""

    def test_default_initialization(self):
        """Test that default value is 0xFFFFFFFF."""
        config = BaseConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = BaseConfig(0x12345678)
        assert config._value == 0x12345678

    def test_zero_initialization(self):
        """Test initialization with zero value."""
        config = BaseConfig(0x00000000)
        assert config._value == 0x00000000

    def test_max_value_initialization(self):
        """Test initialization with maximum 32-bit value."""
        config = BaseConfig(0xFFFFFFFF)
        assert config._value == 0xFFFFFFFF


class TestBaseConfigFromBytes:
    """Test from_bytes() class method."""

    def test_from_bytes_valid_data(self):
        """Test creating config from valid 4-byte data."""
        data = b'\x12\x34\x56\x78'
        config = BaseConfig.from_bytes(data)
        assert config._value == 0x12345678

    def test_from_bytes_all_zeros(self):
        """Test creating config from all zeros."""
        data = b'\x00\x00\x00\x00'
        config = BaseConfig.from_bytes(data)
        assert config._value == 0x00000000

    def test_from_bytes_all_ones(self):
        """Test creating config from all ones."""
        data = b'\xFF\xFF\xFF\xFF'
        config = BaseConfig.from_bytes(data)
        assert config._value == 0xFFFFFFFF

    def test_from_bytes_big_endian(self):
        """Test that from_bytes uses big-endian format."""
        data = b'\x01\x02\x03\x04'
        config = BaseConfig.from_bytes(data)
        # Big-endian: most significant byte first
        assert config._value == 0x01020304

    def test_from_bytes_wrong_length_short(self):
        """Test that from_bytes raises error for data too short."""
        with pytest.raises(ValueError) as exc_info:
            BaseConfig.from_bytes(b'\x12\x34\x56')
        assert "Expected 4 bytes" in str(exc_info.value)
        assert "got 3" in str(exc_info.value)

    def test_from_bytes_wrong_length_long(self):
        """Test that from_bytes raises error for data too long."""
        with pytest.raises(ValueError) as exc_info:
            BaseConfig.from_bytes(b'\x12\x34\x56\x78\x9A')
        assert "Expected 4 bytes" in str(exc_info.value)
        assert "got 5" in str(exc_info.value)

    def test_from_bytes_empty_data(self):
        """Test that from_bytes raises error for empty data."""
        with pytest.raises(ValueError) as exc_info:
            BaseConfig.from_bytes(b'')
        assert "Expected 4 bytes" in str(exc_info.value)


class TestBaseConfigToBytes:
    """Test to_bytes() method."""

    def test_to_bytes_default_value(self):
        """Test converting default value to bytes."""
        config = BaseConfig()
        data = config.to_bytes()
        assert data == b'\xFF\xFF\xFF\xFF'
        assert len(data) == 4

    def test_to_bytes_custom_value(self):
        """Test converting custom value to bytes."""
        config = BaseConfig(0x12345678)
        data = config.to_bytes()
        assert data == b'\x12\x34\x56\x78'
        assert len(data) == 4

    def test_to_bytes_zero_value(self):
        """Test converting zero value to bytes."""
        config = BaseConfig(0x00000000)
        data = config.to_bytes()
        assert data == b'\x00\x00\x00\x00'
        assert len(data) == 4

    def test_to_bytes_big_endian(self):
        """Test that to_bytes uses big-endian format."""
        config = BaseConfig(0x01020304)
        data = config.to_bytes()
        # Big-endian: most significant byte first
        assert data == b'\x01\x02\x03\x04'

    def test_to_bytes_returns_bytes(self):
        """Test that to_bytes returns bytes type."""
        config = BaseConfig(0x12345678)
        data = config.to_bytes()
        assert isinstance(data, bytes)


class TestBaseConfigRoundTrip:
    """Test round-trip conversion (from_bytes -> to_bytes)."""

    def test_round_trip_default_value(self):
        """Test round-trip with default value."""
        original = b'\xFF\xFF\xFF\xFF'
        config = BaseConfig.from_bytes(original)
        result = config.to_bytes()
        assert result == original

    def test_round_trip_custom_value(self):
        """Test round-trip with custom value."""
        original = b'\x12\x34\x56\x78'
        config = BaseConfig.from_bytes(original)
        result = config.to_bytes()
        assert result == original

    def test_round_trip_zero_value(self):
        """Test round-trip with zero value."""
        original = b'\x00\x00\x00\x00'
        config = BaseConfig.from_bytes(original)
        result = config.to_bytes()
        assert result == original

    def test_round_trip_preserves_value(self):
        """Test that round-trip preserves exact value."""
        test_values = [
            b'\x00\x00\x00\x00',
            b'\xFF\xFF\xFF\xFF',
            b'\x12\x34\x56\x78',
            b'\xAA\xBB\xCC\xDD',
            b'\x01\x02\x03\x04',
        ]
        for original in test_values:
            config = BaseConfig.from_bytes(original)
            result = config.to_bytes()
            assert result == original


class TestBaseConfigToDict:
    """Test to_dict() method."""

    def test_to_dict_raises_not_implemented(self):
        """Test that to_dict() raises NotImplementedError on base class."""
        config = BaseConfig()
        with pytest.raises(NotImplementedError) as exc_info:
            config.to_dict()
        assert "Subclasses must implement to_dict()" in str(exc_info.value)


class TestBaseConfigStringRepresentation:
    """Test string representation methods."""

    def test_repr_format(self):
        """Test __repr__ format."""
        config = BaseConfig(0x12345678)
        result = repr(config)
        assert "BaseConfig" in result
        assert "0x12345678" in result

    def test_repr_default_value(self):
        """Test __repr__ with default value."""
        config = BaseConfig()
        result = repr(config)
        assert "BaseConfig" in result
        assert "0xffffffff" in result

    def test_str_format(self):
        """Test __str__ format."""
        config = BaseConfig(0x12345678)
        result = str(config)
        assert "BaseConfig" in result
        assert "0x12345678" in result

    def test_str_default_value(self):
        """Test __str__ with default value."""
        config = BaseConfig()
        result = str(config)
        assert "BaseConfig" in result
        assert "0xffffffff" in result

    def test_repr_str_consistency(self):
        """Test that __repr__ and __str__ return same format for base class."""
        config = BaseConfig(0xABCDEF01)
        assert repr(config) == str(config)

    def test_repr_shows_8_hex_digits(self):
        """Test that __repr__ shows full 8 hex digits."""
        config = BaseConfig(0x00000001)
        result = repr(config)
        # Should pad with zeros to 8 digits
        assert "0x00000001" in result


class TestBaseConfigEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_value_is_32_bit(self):
        """Test that value is stored as 32-bit integer."""
        config = BaseConfig(0xFFFFFFFF)
        assert config._value <= 0xFFFFFFFF
        assert config._value >= 0

    def test_alternating_bits(self):
        """Test with alternating bit pattern."""
        config = BaseConfig(0xAAAAAAAA)
        assert config._value == 0xAAAAAAAA
        data = config.to_bytes()
        assert data == b'\xAA\xAA\xAA\xAA'

    def test_single_bit_set(self):
        """Test with single bit set."""
        config = BaseConfig(0x00000001)
        data = config.to_bytes()
        assert data == b'\x00\x00\x00\x01'

    def test_msb_set(self):
        """Test with most significant bit set."""
        config = BaseConfig(0x80000000)
        data = config.to_bytes()
        assert data == b'\x80\x00\x00\x00'


class TestBaseConfigInheritance:
    """Test that BaseConfig can be subclassed."""

    def test_subclass_creation(self):
        """Test that BaseConfig can be subclassed."""
        class TestConfig(BaseConfig):
            def to_dict(self):
                return {'value': self._value}

        config = TestConfig(0x12345678)
        assert isinstance(config, BaseConfig)
        assert isinstance(config, TestConfig)

    def test_subclass_from_bytes(self):
        """Test that from_bytes works on subclass."""
        class TestConfig(BaseConfig):
            def to_dict(self):
                return {'value': self._value}

        config = TestConfig.from_bytes(b'\x12\x34\x56\x78')
        assert isinstance(config, TestConfig)
        assert config._value == 0x12345678

    def test_subclass_repr_shows_subclass_name(self):
        """Test that __repr__ shows subclass name."""
        class TestConfig(BaseConfig):
            def to_dict(self):
                return {'value': self._value}

        config = TestConfig(0x12345678)
        result = repr(config)
        assert "TestConfig" in result
        assert "BaseConfig" not in result
