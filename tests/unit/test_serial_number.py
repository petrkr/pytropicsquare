"""Tests for TROPIC01 Serial Number parsing.

This module tests:
- Serial number structure parsing from raw bytes
- Field extraction and bit manipulation
- String representations (__str__, __repr__)
- Dictionary conversion
- Error handling for invalid inputs
"""

import pytest
from tropicsquare.chip_id.serial_number import SerialNumber
from tropicsquare.chip_id.constants import SERIAL_NUMBER_SIZE
from tests.fixtures.chip_id_responses import CHIP_ID_SAMPLE


class TestSerialNumberParsing:
    """Test serial number parsing from raw bytes."""

    @pytest.fixture
    def serial_number_data(self):
        """Extract serial number bytes from chip ID sample.

        Serial number is located at bytes 52-67 (16 bytes) in chip ID structure.
        """
        return CHIP_ID_SAMPLE[52:68]

    @pytest.fixture
    def serial_number(self, serial_number_data):
        """Create SerialNumber instance from fixture data."""
        return SerialNumber(serial_number_data)

    def test_serial_number_size_constant(self):
        """Test that SERIAL_NUMBER_SIZE constant is correct."""
        assert SERIAL_NUMBER_SIZE == 16

    def test_parsing_valid_data(self, serial_number_data):
        """Test that valid 16-byte data can be parsed."""
        sn = SerialNumber(serial_number_data)
        assert sn is not None
        assert isinstance(sn, SerialNumber)

    def test_raw_data_stored(self, serial_number, serial_number_data):
        """Test that raw data is stored in the instance."""
        assert serial_number.raw == serial_number_data
        assert len(serial_number.raw) == SERIAL_NUMBER_SIZE

    def test_invalid_length_raises_error(self):
        """Test that data with invalid length raises ValueError."""
        # Too short
        with pytest.raises(ValueError) as exc_info:
            SerialNumber(b'\x00' * 15)
        assert "must be 16 bytes" in str(exc_info.value)
        assert "got 15" in str(exc_info.value)

        # Too long
        with pytest.raises(ValueError) as exc_info:
            SerialNumber(b'\x00' * 17)
        assert "must be 16 bytes" in str(exc_info.value)
        assert "got 17" in str(exc_info.value)

    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            SerialNumber(b'')
        assert "must be 16 bytes" in str(exc_info.value)


class TestSerialNumberFields:
    """Test individual field extraction."""

    @pytest.fixture
    def serial_number_data(self):
        """Extract serial number from chip ID sample."""
        return CHIP_ID_SAMPLE[52:68]

    @pytest.fixture
    def serial_number(self, serial_number_data):
        """Create SerialNumber instance."""
        return SerialNumber(serial_number_data)

    def test_sn_field(self, serial_number, serial_number_data):
        """Test serial number (byte 0) extraction."""
        expected = serial_number_data[0]
        assert serial_number.sn == expected
        assert isinstance(serial_number.sn, int)
        assert 0 <= serial_number.sn <= 0xFF

    def test_fab_id_field(self, serial_number):
        """Test fab_id (12-bit) extraction from bytes 1-3."""
        assert isinstance(serial_number.fab_id, int)
        assert 0 <= serial_number.fab_id <= 0xFFF  # 12-bit max

    def test_part_number_id_field(self, serial_number):
        """Test part_number_id (12-bit) extraction from bytes 1-3."""
        assert isinstance(serial_number.part_number_id, int)
        assert 0 <= serial_number.part_number_id <= 0xFFF  # 12-bit max

    def test_fab_id_and_part_number_bit_manipulation(self, serial_number_data):
        """Test that fab_id and part_number_id are correctly extracted from 24-bit value."""
        # Manually extract the 24-bit value
        fab_data = int.from_bytes(serial_number_data[1:4], "big")
        expected_fab_id = (fab_data >> 12) & 0xFFF
        expected_part_number_id = fab_data & 0xFFF

        sn = SerialNumber(serial_number_data)
        assert sn.fab_id == expected_fab_id
        assert sn.part_number_id == expected_part_number_id

    def test_fab_date_field(self, serial_number, serial_number_data):
        """Test fabrication date (bytes 4-5) extraction."""
        expected = int.from_bytes(serial_number_data[4:6], "big")
        assert serial_number.fab_date == expected
        assert isinstance(serial_number.fab_date, int)

    def test_lot_id_field(self, serial_number, serial_number_data):
        """Test lot ID (bytes 6-10) extraction."""
        expected = serial_number_data[6:11]
        assert serial_number.lot_id == expected
        assert isinstance(serial_number.lot_id, bytes)
        assert len(serial_number.lot_id) == 5

    def test_wafer_id_field(self, serial_number, serial_number_data):
        """Test wafer ID (byte 11) extraction."""
        expected = serial_number_data[11]
        assert serial_number.wafer_id == expected
        assert isinstance(serial_number.wafer_id, int)
        assert 0 <= serial_number.wafer_id <= 0xFF

    def test_x_coord_field(self, serial_number, serial_number_data):
        """Test X coordinate (bytes 12-13) extraction."""
        expected = int.from_bytes(serial_number_data[12:14], "big")
        assert serial_number.x_coord == expected
        assert isinstance(serial_number.x_coord, int)

    def test_y_coord_field(self, serial_number, serial_number_data):
        """Test Y coordinate (bytes 14-15) extraction."""
        expected = int.from_bytes(serial_number_data[14:16], "big")
        assert serial_number.y_coord == expected
        assert isinstance(serial_number.y_coord, int)


class TestSerialNumberStringRepresentation:
    """Test string representation methods."""

    @pytest.fixture
    def serial_number(self):
        """Create SerialNumber with known values for testing."""
        # Create test data with specific known values
        data = bytearray(16)
        data[0] = 0x42  # SN
        # Bytes 1-3: fab_data (24-bit big-endian)
        # fab_id = 0x123, part_number_id = 0x456
        # Combined: (0x123 << 12) | 0x456 = 0x123456
        data[1:4] = (0x123456).to_bytes(3, "big")
        data[4:6] = (0x1234).to_bytes(2, "big")  # fab_date
        data[6:11] = b'\x01\x02\x03\x04\x05'  # lot_id
        data[11] = 0x05  # wafer_id
        data[12:14] = (128).to_bytes(2, "big")  # x_coord
        data[14:16] = (256).to_bytes(2, "big")  # y_coord
        return SerialNumber(bytes(data))

    def test_str_format(self, serial_number):
        """Test __str__ returns compact representation."""
        result = str(serial_number)
        assert isinstance(result, str)
        # Should contain key fields
        assert "SN:0x42" in result
        assert "Fab:0x123" in result
        assert "PN:0x456" in result
        assert "Wafer:0x05" in result
        assert "Coords:(128,256)" in result

    def test_repr_format(self, serial_number):
        """Test __repr__ returns detailed representation."""
        result = repr(serial_number)
        assert isinstance(result, str)
        assert result.startswith("SerialNumber(")
        # Should contain all fields
        assert "sn=0x42" in result
        assert "fab_id=0x123" in result
        assert "part_number_id=0x456" in result
        assert "fab_date=4660" in result  # 0x1234
        assert "lot_id=0102030405" in result
        assert "wafer_id=0x05" in result
        assert "x_coord=128" in result
        assert "y_coord=256" in result

    def test_str_vs_repr(self, serial_number):
        """Test that __str__ is more compact than __repr__."""
        str_result = str(serial_number)
        repr_result = repr(serial_number)
        # repr should be longer (more detailed)
        assert len(repr_result) > len(str_result)


class TestSerialNumberDictConversion:
    """Test dictionary conversion."""

    @pytest.fixture
    def serial_number(self):
        """Create SerialNumber with known values."""
        data = bytearray(16)
        data[0] = 0x42
        data[1:4] = (0x123456).to_bytes(3, "big")
        data[4:6] = (0x1234).to_bytes(2, "big")
        data[6:11] = b'\x01\x02\x03\x04\x05'
        data[11] = 0x05
        data[12:14] = (128).to_bytes(2, "big")
        data[14:16] = (256).to_bytes(2, "big")
        return SerialNumber(bytes(data))

    def test_to_dict_returns_dict(self, serial_number):
        """Test that to_dict() returns a dictionary."""
        result = serial_number.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self, serial_number):
        """Test that dictionary contains all expected fields."""
        result = serial_number.to_dict()
        expected_keys = {
            'sn', 'fab_id', 'part_number_id', 'fab_date',
            'lot_id', 'wafer_id', 'x_coord', 'y_coord'
        }
        assert set(result.keys()) == expected_keys

    def test_to_dict_field_values(self, serial_number):
        """Test that dictionary values match object attributes."""
        result = serial_number.to_dict()
        assert result['sn'] == 0x42
        assert result['fab_id'] == 0x123
        assert result['part_number_id'] == 0x456
        assert result['fab_date'] == 0x1234
        assert result['lot_id'] == '0102030405'  # hex string
        assert result['wafer_id'] == 0x05
        assert result['x_coord'] == 128
        assert result['y_coord'] == 256

    def test_to_dict_lot_id_is_hex_string(self, serial_number):
        """Test that lot_id is converted to hex string in dictionary."""
        result = serial_number.to_dict()
        assert isinstance(result['lot_id'], str)
        assert result['lot_id'] == '0102030405'


class TestSerialNumberEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_zeros(self):
        """Test parsing serial number with all zeros."""
        data = b'\x00' * 16
        sn = SerialNumber(data)
        assert sn.sn == 0
        assert sn.fab_id == 0
        assert sn.part_number_id == 0
        assert sn.fab_date == 0
        assert sn.lot_id == b'\x00' * 5
        assert sn.wafer_id == 0
        assert sn.x_coord == 0
        assert sn.y_coord == 0

    def test_all_ones(self):
        """Test parsing serial number with all 0xFF."""
        data = b'\xFF' * 16
        sn = SerialNumber(data)
        assert sn.sn == 0xFF
        assert sn.fab_id == 0xFFF
        assert sn.part_number_id == 0xFFF
        assert sn.fab_date == 0xFFFF
        assert sn.lot_id == b'\xFF' * 5
        assert sn.wafer_id == 0xFF
        assert sn.x_coord == 0xFFFF
        assert sn.y_coord == 0xFFFF

    def test_coordinates_property(self):
        """Test that coordinates property returns tuple."""
        data = bytearray(16)
        data[12:14] = (100).to_bytes(2, "big")
        data[14:16] = (200).to_bytes(2, "big")
        sn = SerialNumber(bytes(data))
        # Access via string representation
        str_repr = str(sn)
        assert "Coords:(100,200)" in str_repr
