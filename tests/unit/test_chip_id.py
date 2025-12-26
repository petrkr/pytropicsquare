"""Tests for TROPIC01 Chip ID parsing.

This module tests:
- Chip ID structure parsing from raw bytes (128 bytes)
- Field extraction and bit manipulation
- Integration with SerialNumber parsing
- Lookup tables (package types, fabrication locations)
- String representations (__str__, __repr__)
- Dictionary conversion
- Error handling for invalid inputs
"""

import pytest
from tropicsquare.chip_id import ChipId, SerialNumber
from tropicsquare.chip_id.constants import CHIP_ID_SIZE, PACKAGE_TYPES, FAB_LOCATIONS
from tests.fixtures.chip_id_responses import CHIP_ID_SAMPLE


class TestChipIdParsing:
    """Test chip ID parsing from raw bytes."""

    def test_chip_id_size_constant(self):
        """Test that CHIP_ID_SIZE constant is correct."""
        assert CHIP_ID_SIZE == 128

    def test_parsing_valid_data(self):
        """Test that valid 128-byte data can be parsed."""
        chip_id = ChipId(CHIP_ID_SAMPLE)
        assert chip_id is not None
        assert isinstance(chip_id, ChipId)

    def test_raw_data_stored(self):
        """Test that raw data is stored in the instance."""
        chip_id = ChipId(CHIP_ID_SAMPLE)
        assert chip_id.raw == CHIP_ID_SAMPLE
        assert len(chip_id.raw) == CHIP_ID_SIZE

    def test_invalid_length_raises_error(self):
        """Test that data with invalid length raises ValueError."""
        # Too short
        with pytest.raises(ValueError) as exc_info:
            ChipId(b'\x00' * 127)
        assert "must be 128 bytes" in str(exc_info.value)
        assert "got 127" in str(exc_info.value)

        # Too long
        with pytest.raises(ValueError) as exc_info:
            ChipId(b'\x00' * 129)
        assert "must be 128 bytes" in str(exc_info.value)
        assert "got 129" in str(exc_info.value)

    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ChipId(b'')
        assert "must be 128 bytes" in str(exc_info.value)


class TestChipIdBasicFields:
    """Test basic field extraction."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance from fixture data."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_chip_id_version(self, chip_id):
        """Test chip ID version (bytes 0-3) extraction."""
        expected = tuple(CHIP_ID_SAMPLE[0:4])
        assert chip_id.chip_id_version == expected
        assert isinstance(chip_id.chip_id_version, tuple)
        assert len(chip_id.chip_id_version) == 4

    def test_fl_chip_info(self, chip_id):
        """Test factory level chip info (bytes 4-19) extraction."""
        expected = CHIP_ID_SAMPLE[4:20]
        assert chip_id.fl_chip_info == expected
        assert isinstance(chip_id.fl_chip_info, bytes)
        assert len(chip_id.fl_chip_info) == 16

    def test_func_test_info(self, chip_id):
        """Test functional test info (bytes 20-27) extraction."""
        expected = CHIP_ID_SAMPLE[20:28]
        assert chip_id.func_test_info == expected
        assert isinstance(chip_id.func_test_info, bytes)
        assert len(chip_id.func_test_info) == 8

    def test_silicon_rev(self, chip_id):
        """Test silicon revision (bytes 28-31) extraction."""
        # Silicon revision is ASCII string, null-terminated
        assert isinstance(chip_id.silicon_rev, str)
        # Should not contain null bytes
        assert '\x00' not in chip_id.silicon_rev

    def test_package_type_id(self, chip_id):
        """Test package type ID (bytes 32-33) extraction."""
        expected = int.from_bytes(CHIP_ID_SAMPLE[32:34], "big")
        assert chip_id.package_type_id == expected
        assert isinstance(chip_id.package_type_id, int)

    def test_package_type_name_lookup(self, chip_id):
        """Test package type name lookup from ID."""
        assert isinstance(chip_id.package_type_name, str)
        # Should be either known type or "Unknown"
        if chip_id.package_type_id in PACKAGE_TYPES:
            assert chip_id.package_type_name == PACKAGE_TYPES[chip_id.package_type_id]
        else:
            assert chip_id.package_type_name == "Unknown"


class TestChipIdProvisioningFields:
    """Test provisioning-related field extraction and bit manipulation."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_provisioning_version(self, chip_id):
        """Test provisioning version (8-bit) extraction from bytes 36-39."""
        prov_data = int.from_bytes(CHIP_ID_SAMPLE[36:40], "big")
        expected = (prov_data >> 24) & 0xFF
        assert chip_id.provisioning_version == expected
        assert isinstance(chip_id.provisioning_version, int)
        assert 0 <= chip_id.provisioning_version <= 0xFF

    def test_fab_id(self, chip_id):
        """Test fab_id (12-bit) extraction from bytes 36-39."""
        prov_data = int.from_bytes(CHIP_ID_SAMPLE[36:40], "big")
        expected = (prov_data >> 12) & 0xFFF
        assert chip_id.fab_id == expected
        assert isinstance(chip_id.fab_id, int)
        assert 0 <= chip_id.fab_id <= 0xFFF

    def test_part_number_id(self, chip_id):
        """Test part_number_id (12-bit) extraction from bytes 36-39."""
        prov_data = int.from_bytes(CHIP_ID_SAMPLE[36:40], "big")
        expected = prov_data & 0xFFF
        assert chip_id.part_number_id == expected
        assert isinstance(chip_id.part_number_id, int)
        assert 0 <= chip_id.part_number_id <= 0xFFF

    def test_provisioning_bit_manipulation(self, chip_id):
        """Test that provisioning fields are correctly extracted from 32-bit value."""
        prov_data = int.from_bytes(CHIP_ID_SAMPLE[36:40], "big")

        # Verify bit positions
        prov_ver = (prov_data >> 24) & 0xFF
        fab_id = (prov_data >> 12) & 0xFFF
        part_num = prov_data & 0xFFF

        assert chip_id.provisioning_version == prov_ver
        assert chip_id.fab_id == fab_id
        assert chip_id.part_number_id == part_num

    def test_fab_name_lookup(self, chip_id):
        """Test fabrication facility name lookup from ID."""
        assert isinstance(chip_id.fab_name, str)
        if chip_id.fab_id in FAB_LOCATIONS:
            assert chip_id.fab_name == FAB_LOCATIONS[chip_id.fab_id]
        else:
            assert chip_id.fab_name == "Unknown"

    def test_provisioning_date(self, chip_id):
        """Test provisioning date (bytes 40-41) extraction."""
        expected = int.from_bytes(CHIP_ID_SAMPLE[40:42], "big")
        assert chip_id.provisioning_date == expected
        assert isinstance(chip_id.provisioning_date, int)


class TestChipIdVersionFields:
    """Test version-related fields."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_hsm_version(self, chip_id):
        """Test HSM version (bytes 42-45) extraction."""
        expected = tuple(CHIP_ID_SAMPLE[42:46])
        assert chip_id.hsm_version == expected
        assert isinstance(chip_id.hsm_version, tuple)
        assert len(chip_id.hsm_version) == 4

    def test_prog_version(self, chip_id):
        """Test program version (bytes 46-49) extraction."""
        expected = tuple(CHIP_ID_SAMPLE[46:50])
        assert chip_id.prog_version == expected
        assert isinstance(chip_id.prog_version, tuple)
        assert len(chip_id.prog_version) == 4


class TestChipIdSerialNumberIntegration:
    """Test integration with SerialNumber parsing."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_serial_number_is_serial_number_instance(self, chip_id):
        """Test that serial_number is SerialNumber instance."""
        assert isinstance(chip_id.serial_number, SerialNumber)

    def test_serial_number_data_matches(self, chip_id):
        """Test that serial number data matches bytes 52-67."""
        expected_data = CHIP_ID_SAMPLE[52:68]
        assert chip_id.serial_number.raw == expected_data

    def test_serial_number_fields_accessible(self, chip_id):
        """Test that serial number fields are accessible through chip_id."""
        sn = chip_id.serial_number
        assert hasattr(sn, 'sn')
        assert hasattr(sn, 'fab_id')
        assert hasattr(sn, 'part_number_id')
        assert hasattr(sn, 'wafer_id')
        assert hasattr(sn, 'x_coord')
        assert hasattr(sn, 'y_coord')


class TestChipIdRemainingFields:
    """Test remaining chip ID fields."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_part_num_data(self, chip_id):
        """Test part number data (bytes 68-83) extraction."""
        expected = CHIP_ID_SAMPLE[68:84]
        assert chip_id.part_num_data == expected
        assert isinstance(chip_id.part_num_data, bytes)
        assert len(chip_id.part_num_data) == 16

    def test_prov_template_version(self, chip_id):
        """Test provisioning template version (bytes 84-85) extraction."""
        expected = int.from_bytes(CHIP_ID_SAMPLE[84:86], "big")
        assert chip_id.prov_template_version == expected
        assert isinstance(chip_id.prov_template_version, int)

    def test_prov_template_tag(self, chip_id):
        """Test provisioning template tag (bytes 86-89) extraction."""
        expected = CHIP_ID_SAMPLE[86:90]
        assert chip_id.prov_template_tag == expected
        assert isinstance(chip_id.prov_template_tag, bytes)
        assert len(chip_id.prov_template_tag) == 4

    def test_prov_spec_version(self, chip_id):
        """Test provisioning spec version (bytes 90-91) extraction."""
        expected = int.from_bytes(CHIP_ID_SAMPLE[90:92], "big")
        assert chip_id.prov_spec_version == expected
        assert isinstance(chip_id.prov_spec_version, int)

    def test_prov_spec_tag(self, chip_id):
        """Test provisioning spec tag (bytes 92-95) extraction."""
        expected = CHIP_ID_SAMPLE[92:96]
        assert chip_id.prov_spec_tag == expected
        assert isinstance(chip_id.prov_spec_tag, bytes)
        assert len(chip_id.prov_spec_tag) == 4

    def test_batch_id(self, chip_id):
        """Test batch ID (bytes 96-100) extraction."""
        expected = CHIP_ID_SAMPLE[96:101]
        assert chip_id.batch_id == expected
        assert isinstance(chip_id.batch_id, bytes)
        assert len(chip_id.batch_id) == 5


class TestChipIdStringRepresentation:
    """Test string representation methods."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_str_format(self, chip_id):
        """Test __str__ returns multi-line representation."""
        result = str(chip_id)
        assert isinstance(result, str)
        assert "TROPIC01 Chip ID:" in result
        assert "Chip ID Version:" in result
        assert "Silicon Revision:" in result
        assert "Package Type:" in result
        assert "Fabrication:" in result
        assert "Serial Number:" in result

    def test_str_contains_values(self, chip_id):
        """Test that __str__ contains actual values."""
        result = str(chip_id)
        assert chip_id.package_type_name in result
        assert chip_id.fab_name in result
        assert chip_id.batch_id.hex() in result

    def test_repr_format(self, chip_id):
        """Test __repr__ returns compact representation."""
        result = repr(chip_id)
        assert isinstance(result, str)
        assert result.startswith("ChipId(")
        assert "package=" in result
        assert "fab=" in result
        assert "sn=" in result

    def test_str_is_multiline(self, chip_id):
        """Test that __str__ is multi-line."""
        result = str(chip_id)
        lines = result.split('\n')
        assert len(lines) > 1

    def test_repr_is_single_line(self, chip_id):
        """Test that __repr__ is single line."""
        result = repr(chip_id)
        assert '\n' not in result


class TestChipIdDictConversion:
    """Test dictionary conversion."""

    @pytest.fixture
    def chip_id(self):
        """Create ChipId instance."""
        return ChipId(CHIP_ID_SAMPLE)

    def test_to_dict_returns_dict(self, chip_id):
        """Test that to_dict() returns a dictionary."""
        result = chip_id.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self, chip_id):
        """Test that dictionary contains all expected fields."""
        result = chip_id.to_dict()
        expected_keys = {
            'chip_id_version', 'fl_chip_info', 'func_test_info', 'silicon_rev',
            'package_type_id', 'package_type_name', 'provisioning_version',
            'fab_id', 'fab_name', 'part_number_id', 'provisioning_date',
            'hsm_version', 'prog_version', 'serial_number', 'part_num_data',
            'prov_template_version', 'prov_template_tag', 'prov_spec_version',
            'prov_spec_tag', 'batch_id'
        }
        assert set(result.keys()) == expected_keys

    def test_to_dict_serial_number_is_nested_dict(self, chip_id):
        """Test that serial_number is converted to nested dictionary."""
        result = chip_id.to_dict()
        assert isinstance(result['serial_number'], dict)
        # Should have serial number fields
        assert 'sn' in result['serial_number']
        assert 'fab_id' in result['serial_number']

    def test_to_dict_bytes_are_hex_strings(self, chip_id):
        """Test that bytes fields are converted to hex strings."""
        result = chip_id.to_dict()
        assert isinstance(result['fl_chip_info'], str)
        assert isinstance(result['func_test_info'], str)
        assert isinstance(result['part_num_data'], str)
        assert isinstance(result['batch_id'], str)

    def test_to_dict_tuples_are_lists(self, chip_id):
        """Test that tuple fields are converted to lists."""
        result = chip_id.to_dict()
        assert isinstance(result['chip_id_version'], list)
        assert isinstance(result['hsm_version'], list)
        assert isinstance(result['prog_version'], list)


class TestChipIdEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_zeros(self):
        """Test parsing chip ID with all zeros."""
        data = b'\x00' * 128
        chip_id = ChipId(data)
        assert chip_id.chip_id_version == (0, 0, 0, 0)
        assert chip_id.package_type_id == 0
        assert chip_id.provisioning_version == 0
        assert chip_id.fab_id == 0
        assert chip_id.part_number_id == 0

    def test_all_ones(self):
        """Test parsing chip ID with all 0xFF."""
        data = b'\xFF' * 128
        chip_id = ChipId(data)
        assert chip_id.chip_id_version == (0xFF, 0xFF, 0xFF, 0xFF)
        assert chip_id.package_type_id == 0xFFFF
        assert chip_id.provisioning_version == 0xFF
        assert chip_id.fab_id == 0xFFF
        assert chip_id.part_number_id == 0xFFF

    def test_unknown_package_type(self):
        """Test that unknown package type ID returns 'Unknown'."""
        data = bytearray(128)
        # Set package type to invalid value
        data[32:34] = (0x9999).to_bytes(2, "big")
        chip_id = ChipId(bytes(data))
        assert chip_id.package_type_name == "Unknown"

    def test_unknown_fab_location(self):
        """Test that unknown fab ID returns 'Unknown'."""
        data = bytearray(128)
        # Set fab_id to invalid value (bits 12-23 of bytes 36-39)
        # prov_data = [0:8bits prov_ver][8:12bits fab_id][12:12bits part_num]
        prov_data = (0x00 << 24) | (0x999 << 12) | 0x000
        data[36:40] = prov_data.to_bytes(4, "big")
        chip_id = ChipId(bytes(data))
        assert chip_id.fab_name == "Unknown"

    def test_silicon_rev_with_nulls(self):
        """Test silicon revision with null bytes is trimmed."""
        data = bytearray(128)
        data[28:32] = b'ABCD'
        chip_id = ChipId(bytes(data))
        assert chip_id.silicon_rev == 'ABCD'

        # With null termination
        data[28:32] = b'AB\x00\x00'
        chip_id = ChipId(bytes(data))
        assert chip_id.silicon_rev == 'AB'
        assert '\x00' not in chip_id.silicon_rev
