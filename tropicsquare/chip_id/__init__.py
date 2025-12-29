"""TROPIC01 Chip ID parsing module

This module provides classes and constants for parsing and representing
the TROPIC01 chip identification structure.

Main exports:
    - ChipId: Main chip ID structure parser
    - SerialNumber: Serial number structure parser
    - Constants available from tropicsquare.chip_id.constants

Example:
    >>> from tropicsquare.chip_id import ChipId
    >>> chip_id = ChipId(raw_chip_id_bytes)
    >>> print(chip_id.package_type_name)
    'QFN32'
    >>> print(chip_id.fab_name)
    'EPS Brno'
    >>> print(chip_id.serial_number)
    SN:0x42 Fab:0x001 PN:0x123 Wafer:0x05 Coords:(128,256)
"""

from tropicsquare.chip_id.serial_number import SerialNumber
from tropicsquare.chip_id.constants import (
    CHIP_ID_SIZE,
    PACKAGE_TYPES,
    FAB_LOCATIONS
)


class ChipId:
    """TROPC01 Chip ID structure parser

        This class parses the 128-byte chip identification structure that contains
        comprehensive information about the chip including manufacturing data,
        provisioning information, firmware versions, and serial number.

        The structure follows the lt_chip_id_t layout from libtropic with all
        fields properly parsed and exposed as attributes.

        **Structure layout (128 bytes total):**

        - Bytes 0-3: Chip ID version (4 bytes)
        - Bytes 4-19: Factory level chip info (16 bytes)
        - Bytes 20-27: Functional test info (8 bytes)
        - Bytes 28-31: Silicon revision (4 bytes, ASCII)
        - Bytes 32-33: Package type ID (2 bytes, big-endian)
        - Bytes 34-35: Reserved field 1 (2 bytes)
        - Bytes 36-39: Provisioning info - version/fab/part number (4 bytes, big-endian)
        - Bytes 40-41: Provisioning date (2 bytes, big-endian)
        - Bytes 42-45: HSM version (4 bytes)
        - Bytes 46-49: Program version (4 bytes)
        - Bytes 50-51: Reserved field 2 (2 bytes)
        - Bytes 52-67: Serial number structure (16 bytes)
        - Bytes 68-83: Part number data (16 bytes)
        - Bytes 84-85: Provisioning template version (2 bytes, big-endian)
        - Bytes 86-89: Provisioning template tag (4 bytes)
        - Bytes 90-91: Provisioning specification version (2 bytes, big-endian)
        - Bytes 92-95: Provisioning specification tag (4 bytes)
        - Bytes 96-100: Batch ID (5 bytes)
        - Bytes 101-103: Reserved field 3 (3 bytes)
        - Bytes 104-127: Reserved field 4 / Padding (24 bytes)

        Attributes:

            raw (bytes): Original raw chip ID data (128 bytes)
            chip_id_version (tuple): Chip ID version as 4-element tuple
            fl_chip_info (bytes): Factory level chip information (16 bytes)
            func_test_info (bytes): Functional test information (8 bytes)
            silicon_rev (str): Silicon revision (ASCII string, null-terminated)
            package_type_id (int): Package type identifier
            package_type_name (str): Human-readable package type name
            provisioning_version (int): Provisioning version number (8-bit)
            fab_id (int): Fabrication facility ID (12-bit)
            fab_name (str): Human-readable fabrication facility name
            part_number_id (int): Part number identifier (12-bit)
            provisioning_date (int): Provisioning date value
            hsm_version (tuple): HSM version as 4-element tuple
            prog_version (tuple): Program version as 4-element tuple
            serial_number (SerialNumber): Parsed serial number structure
            part_num_data (bytes): Part number data (16 bytes)
            prov_template_version (int): Provisioning template version
            prov_template_tag (bytes): Provisioning template tag (4 bytes)
            prov_spec_version (int): Provisioning specification version
            prov_spec_tag (bytes): Provisioning specification tag (4 bytes)
            batch_id (bytes): Batch identifier (5 bytes)
    """

    def __init__(self, data: bytes):
        """Parse chip ID from raw bytes

            :param data: Raw chip ID bytes (must be exactly 128 bytes)

            :raises ValueError: If data length is not 128 bytes
        """
        if len(data) != CHIP_ID_SIZE:
            raise ValueError(f"Chip ID must be {CHIP_ID_SIZE} bytes, got {len(data)}")

        self.raw = data

        # Bytes 0-3: Chip ID version (4 bytes)
        self.chip_id_version = tuple(data[0:4])

        # Bytes 4-19: Factory level chip info (16 bytes)
        self.fl_chip_info = data[4:20]

        # Bytes 20-27: Functional test info (8 bytes)
        self.func_test_info = data[20:28]

        # Bytes 28-31: Silicon revision (4 bytes, ASCII)
        self.silicon_rev = data[28:32].decode('ascii', 'ignore').rstrip('\x00')

        # Bytes 32-33: Package type ID (2 bytes, big-endian)
        self.package_type_id = int.from_bytes(data[32:34], "big")
        self.package_type_name = PACKAGE_TYPES.get(self.package_type_id, "Unknown")

        # Bytes 34-35: Reserved field 1 (skipped)

        # Bytes 36-39: Provisioning info (4 bytes, big-endian)
        # Layout: [prov_ver:8][fab_id:12][part_num:12] = 32 bits
        prov_data = int.from_bytes(data[36:40], "big")
        self.provisioning_version = (prov_data >> 24) & 0xFF     # Bits 24-31
        self.fab_id = (prov_data >> 12) & 0xFFF                  # Bits 12-23
        self.part_number_id = prov_data & 0xFFF                  # Bits 0-11
        self.fab_name = FAB_LOCATIONS.get(self.fab_id, "Unknown")

        # Bytes 40-41: Provisioning date (2 bytes, big-endian)
        self.provisioning_date = int.from_bytes(data[40:42], "big")

        # Bytes 42-45: HSM version (4 bytes)
        self.hsm_version = tuple(data[42:46])

        # Bytes 46-49: Program version (4 bytes)
        self.prog_version = tuple(data[46:50])

        # Bytes 50-51: Reserved field 2 (skipped)

        # Bytes 52-67: Serial number (16 bytes)
        self.serial_number = SerialNumber(data[52:68])

        # Bytes 68-83: Part number data (16 bytes)
        self.part_num_data = data[68:84]

        # Bytes 84-85: Provisioning template version (2 bytes, big-endian)
        self.prov_template_version = int.from_bytes(data[84:86], "big")

        # Bytes 86-89: Provisioning template tag (4 bytes)
        self.prov_template_tag = data[86:90]

        # Bytes 90-91: Provisioning specification version (2 bytes, big-endian)
        self.prov_spec_version = int.from_bytes(data[90:92], "big")

        # Bytes 92-95: Provisioning specification tag (4 bytes)
        self.prov_spec_tag = data[92:96]

        # Bytes 96-100: Batch ID (5 bytes)
        self.batch_id = data[96:101]

        # Bytes 101-103: Reserved field 3 (skipped)
        # Bytes 104-127: Reserved field 4 / Padding (skipped)

    def __str__(self) -> str:
        """Get human-readable multi-line string representation

            :returns: Multi-line formatted string with key chip ID information
        """
        lines = [
            "TROPIC01 Chip ID:",
            f"  Chip ID Version: {'.'.join(map(str, self.chip_id_version))}",
            f"  Silicon Revision: {self.silicon_rev}",
            f"  Package Type: {self.package_type_name} (0x{self.package_type_id:04X})",
            f"  Fabrication: {self.fab_name} (0x{self.fab_id:03X})",
            f"  Part Number ID: 0x{self.part_number_id:03X}",
            f"  HSM Version: {'.'.join(map(str, self.hsm_version))}",
            f"  Program Version: {'.'.join(map(str, self.prog_version))}",
            f"  Serial Number: {self.serial_number}",
            f"  Batch ID: {self.batch_id.hex()}",
        ]
        return '\n'.join(lines)

    def __repr__(self) -> str:
        """Get detailed string representation for debugging

            :returns: Detailed representation with class name
        """
        return f"ChipId(package={self.package_type_name}, fab={self.fab_name}, sn={self.serial_number.sn:02X})"

    def to_dict(self) -> dict:
        """Convert chip ID to dictionary representation

            :returns: Dictionary containing all chip ID fields with nested serial number
        """
        return {
            'chip_id_version': list(self.chip_id_version),
            'fl_chip_info': self.fl_chip_info.hex(),
            'func_test_info': self.func_test_info.hex(),
            'silicon_rev': self.silicon_rev,
            'package_type_id': self.package_type_id,
            'package_type_name': self.package_type_name,
            'provisioning_version': self.provisioning_version,
            'fab_id': self.fab_id,
            'fab_name': self.fab_name,
            'part_number_id': self.part_number_id,
            'provisioning_date': self.provisioning_date,
            'hsm_version': list(self.hsm_version),
            'prog_version': list(self.prog_version),
            'serial_number': self.serial_number.to_dict(),
            'part_num_data': self.part_num_data.hex(),
            'prov_template_version': self.prov_template_version,
            'prov_template_tag': self.prov_template_tag.hex(),
            'prov_spec_version': self.prov_spec_version,
            'prov_spec_tag': self.prov_spec_tag.hex(),
            'batch_id': self.batch_id.hex(),
        }
