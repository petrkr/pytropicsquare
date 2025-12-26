# PyTropicSquare

Python library for communicating with the Tropic Square TROPIC01 secure element chip.

## Overview

PyTropicSquare provides a comprehensive Python interface for the TROPIC01 secure element, supporting both CPython and MicroPython environments. The library implements the complete communication protocol stack for secure operations including cryptographic functions, key management, and secure data storage.

## Features

- **Dual Platform Support**: Works with both CPython (using the `cryptography` library) and MicroPython (with embedded crypto implementations)
- **Secure Communication**: X25519 key exchange with HKDF key derivation and AES-GCM encryption
- **Cryptographic Operations**: 
  - ECDSA signing (P256 curve)
  - EdDSA signing (Ed25519 curve)
  - ECC key generation and management
- **Secure Storage**: Memory slots for data storage (up to 444 bytes per slot)
- **Chip Identification**: Parsed chip ID with manufacturing details (package type, fab location, serial number, wafer coordinates)
- **Additional Features**:
  - True random number generation
  - Monotonic counters
  - MAC and destroy operations
  - Certificate and public key extraction

## Installation

### From PyPI (when available)
```bash
pip install pytropicsquare
```

### From Source
```bash
git clone https://github.com/petrkr/pytropicsquare.git
cd pytropicsquare
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Example
```python
from tropicsquare import TropicSquare
from tropicsquare.transports.spi import SPITransport

# Initialize with your SPI interface and CS pin
transport = SPITransport(spi, cs)
ts = TropicSquare(transport)

# Get chip information
print(ts.chipid)  # Human-readable output
print(f"Package: {chip_id.package_type_name}")
print(f"Fabrication: {chip_id.fab_name}")
print(f"SPECT FW: {ts.spect_fw_version}")
print(f"RISC-V FW: {ts.riscv_fw_version}")

# Start secure session (requires pairing keys)
ts.start_secure_session(key_index, private_key, public_key)

# Perform operations
random_data = ts.get_random(32)
ping_response = ts.ping(b"Hello TROPIC01!")

# Generate and use ECC keys
ts.ecc_key_generate(slot=0, curve=ECC_CURVE_ED25519)
signature = ts.eddsa_sign(slot=0, message=b"Sign this message")
```

## Chip Information

The library provides detailed chip identification and manufacturing data through parsed structures:

```python
# Get parsed chip ID
chip_id = ts.chipid

# Access chip information
print(chip_id)  # Multi-line human-readable output

# Individual fields
print(f"Package Type: {chip_id.package_type_name}")      # "QFN32", "Bare Silicon"
print(f"Silicon Revision: {chip_id.silicon_rev}")        # e.g., "ACAB"
print(f"Fabrication Facility: {chip_id.fab_name}")       # "EPS Brno", "Tropic Square Lab"
print(f"Part Number ID: 0x{chip_id.part_number_id:03X}")
print(f"HSM Version: {'.'.join(map(str, chip_id.hsm_version))}")
print(f"Batch ID: {chip_id.batch_id.hex()}")

# Serial number details
sn = chip_id.serial_number
print(f"Serial Number: 0x{sn.sn:02X}")
print(f"Fab ID: 0x{sn.fab_id:03X}")
print(f"Wafer ID: 0x{sn.wafer_id:02X}")
print(f"Wafer Coordinates: ({sn.x_coord}, {sn.y_coord})")
print(f"Lot ID: {sn.lot_id.hex()}")

# Export to dictionary (useful for JSON serialization)
chip_dict = chip_id.to_dict()

# Access raw bytes if needed
raw_chip_id = chip_id.raw  # 128 bytes
```

## Architecture

The library is structured in three protocol layers:

- **L1 (Transport)**: SPI communication layer
- **L2 (Protocol)**: Chip communication with CRC validation and session management  
- **L3 (Commands)**: High-level cryptographic and utility functions

## API Reference

### Core Classes

- `TropicSquare`: Abstract base class with protocol implementation
- `TropicSquareCPython`: CPython implementation
- `TropicSquareMicroPython`: MicroPython implementation

### Chip Information Classes

- `ChipId`: Parsed chip identification structure (128 bytes)
  - Properties: `package_type_name`, `fab_name`, `silicon_rev`, `serial_number`, `hsm_version`, `prog_version`, `batch_id`, and more
  - Methods: `to_dict()` for JSON export, `__str__()` for human-readable output
- `SerialNumber`: Chip serial number with manufacturing details (16 bytes)
  - Properties: `sn`, `fab_id`, `part_number_id`, `wafer_id`, `x_coord`, `y_coord`, `lot_id`
  - Methods: `to_dict()` for JSON export

### Key Methods

#### Session Management
- `start_secure_session(key_index, private_key, public_key)`: Establish encrypted session
- `abort_secure_session()`: Terminate current session

#### Cryptographic Operations
- `get_random(nbytes)`: Generate true random bytes
- `ecc_key_generate(slot, curve)`: Generate ECC keypair
- `ecdsa_sign(slot, hash)`: Sign hash with P256 key
- `eddsa_sign(slot, message)`: Sign message with Ed25519 key

#### Data Storage
- `mem_data_write(data, slot)`: Write data to memory slot
- `mem_data_read(slot)`: Read data from memory slot
- `mem_data_erase(slot)`: Erase memory slot

#### Utility Functions
- `ping(data)`: Echo test
- `get_log()`: Retrieve chip logs
- `mcounter_init/update/get()`: Monotonic counter operations

## Examples

See the `examples/` directory for complete usage examples:
- `esp32-hello.py`: MicroPython example for ESP32

## Requirements

- Python 3.9+
- `cryptography` library (CPython only)

## Documentation

Full API documentation is available at: [GitHub Pages](https://petrkr.github.io/pytropicsquare/)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Petr Kracik (petrkr@petrkr.net)
