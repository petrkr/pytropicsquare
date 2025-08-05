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

### CPython Example
```python
from tropicsquare.ports.cpython import TropicSquareCPython

# Initialize with your SPI interface and CS pin
ts = TropicSquareCPython(spi, cs_pin)

# Get chip information
print(f"Chip ID: {ts.chipid.hex()}")
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

### MicroPython Example
```python
from tropicsquare.ports.micropython import TropicSquareMicroPython
from machine import SPI, Pin

# Initialize SPI and CS pin
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0, 
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5, Pin.OUT)

ts = TropicSquareMicroPython(spi, cs)

# Same API as CPython version
print(f"Chip ID: {ts.chipid.hex()}")
# ... rest of operations identical
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
