"""TROPIC01 Serial Number structure parser

This module provides the SerialNumber class for parsing and representing
the serial number structure embedded in TROPIC01 chip ID.

Based on lt_ser_num_t structure from libtropic.
"""

from tropicsquare.chip_id.constants import SERIAL_NUMBER_SIZE


class SerialNumber:
    """Serial number structure parser for TROPIC01 chip

    This class parses the 16-byte serial number structure that contains
    chip manufacturing information including fabrication facility, wafer
    coordinates, and unique identifiers.

    Structure layout (16 bytes total):
    - Byte 0: Serial number (8 bits)
    - Bytes 1-3: fab_data containing:
      - Fab ID (12 bits, bits 12-23)
      - Part number ID (12 bits, bits 0-11)
    - Bytes 4-5: Fabrication date (16 bits, little-endian)
    - Bytes 6-10: Lot ID (40 bits)
    - Byte 11: Wafer ID (8 bits)
    - Bytes 12-13: X coordinate on wafer (16 bits, little-endian)
    - Bytes 14-15: Y coordinate on wafer (16 bits, little-endian)

    Attributes:
        raw (bytes): Original raw serial number data (16 bytes)
        sn (int): Serial number (8-bit)
        fab_id (int): Fabrication facility ID (12-bit)
        part_number_id (int): Part number identifier (12-bit)
        fab_date (int): Fabrication date as integer
        lot_id (bytes): Manufacturing lot identifier (5 bytes)
        wafer_id (int): Wafer identifier (8-bit)
        x_coord (int): X coordinate on wafer (16-bit)
        y_coord (int): Y coordinate on wafer (16-bit)
    """

    def __init__(self, data: bytes):
        """Parse serial number from raw bytes

        Args:
            data: Raw serial number bytes (must be exactly 16 bytes)

        Raises:
            ValueError: If data length is not 16 bytes
        """
        if len(data) != SERIAL_NUMBER_SIZE:
            raise ValueError(f"Serial number must be {SERIAL_NUMBER_SIZE} bytes, got {len(data)}")

        self.raw = data

        # Byte 0: Serial number
        self.sn = data[0]

        # Bytes 1-3: fab_data contains fab_id (12 bits) + part_number_id (12 bits)
        # Big-endian 24-bit value
        fab_data = int.from_bytes(data[1:4], "big")
        self.fab_id = (fab_data >> 12) & 0xFFF           # Upper 12 bits
        self.part_number_id = fab_data & 0xFFF           # Lower 12 bits

        # Bytes 4-5: Fabrication date (16-bit big-endian)
        self.fab_date = int.from_bytes(data[4:6], "big")

        # Bytes 6-10: Lot ID (40 bits / 5 bytes)
        self.lot_id = data[6:11]

        # Byte 11: Wafer ID
        self.wafer_id = data[11]

        # Bytes 12-13: X coordinate (16-bit big-endian)
        self.x_coord = int.from_bytes(data[12:14], "big")

        # Bytes 14-15: Y coordinate (16-bit big-endian)
        self.y_coord = int.from_bytes(data[14:16], "big")

    def __str__(self) -> str:
        """Get human-readable string representation

        Returns:
            Compact string representation with key serial number fields
        """
        return (f"SN:0x{self.sn:02X} Fab:0x{self.fab_id:03X} PN:0x{self.part_number_id:03X} "
                f"Wafer:0x{self.wafer_id:02X} Coords:({self.x_coord},{self.y_coord})")

    def __repr__(self) -> str:
        """Get detailed string representation for debugging

        Returns:
            Detailed representation including all fields
        """
        return (f"SerialNumber(sn=0x{self.sn:02X}, fab_id=0x{self.fab_id:03X}, "
                f"part_number_id=0x{self.part_number_id:03X}, fab_date={self.fab_date}, "
                f"lot_id={self.lot_id.hex()}, wafer_id=0x{self.wafer_id:02X}, "
                f"x_coord={self.x_coord}, y_coord={self.y_coord})")

    def to_dict(self) -> dict:
        """Convert serial number to dictionary representation

        Returns:
            Dictionary containing all serial number fields with hex-encoded bytes
        """
        return {
            'sn': self.sn,
            'fab_id': self.fab_id,
            'part_number_id': self.part_number_id,
            'fab_date': self.fab_date,
            'lot_id': self.lot_id.hex(),
            'wafer_id': self.wafer_id,
            'x_coord': self.x_coord,
            'y_coord': self.y_coord,
        }
