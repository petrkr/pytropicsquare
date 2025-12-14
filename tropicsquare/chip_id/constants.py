"""TROPIC01 Chip ID related constants

This module contains constants for parsing and interpreting TROPIC01 chip ID structure,
including package types, fabrication facility IDs, and chip ID structure size.

Based on: https://github.com/tropicsquare/libtropic/blob/master/include/libtropic_common.h
"""

# Chip ID structure size
CHIP_ID_SIZE = 128  #< Total size of lt_chip_id_t structure in bytes (includes 24-byte padding)

# Serial number structure size
SERIAL_NUMBER_SIZE = 16  #< Total size of lt_ser_num_t structure in bytes

# Package Type IDs
CHIP_PKG_BARE_SILICON_ID = 0x8000  #< Package type ID for bare silicon
CHIP_PKG_QFN32_ID = 0x80AA         #< Package type ID for QFN32 package

#< Mapping of package type IDs to human-readable names
PACKAGE_TYPES = {
    CHIP_PKG_BARE_SILICON_ID: "Bare Silicon",
    CHIP_PKG_QFN32_ID: "QFN32",
}

# Fabrication Facility IDs
FAB_ID_TROPIC_SQUARE_LAB = 0xF00  #< Fab ID of Tropic Square Lab
FAB_ID_EPS_BRNO = 0x001           #< Fab ID of Production line #1 (EPS Brno)

#< Mapping of fabrication facility IDs to human-readable names
FAB_LOCATIONS = {
    FAB_ID_TROPIC_SQUARE_LAB: "Tropic Square Lab",
    FAB_ID_EPS_BRNO: "EPS Brno",
}
