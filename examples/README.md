# PyTropicSquare Examples

This directory contains comprehensive examples for the PyTropicSquare library, organized by complexity and feature area.

## Installation and Setup

### For Development (Recommended)

Install the library in **editable mode** using your virtual environment. This creates a symlink, so all code changes are immediately available without reinstalling:

```bash
git clone https://github.com/petrkr/pytropicsquare
cd pytropicsquare

# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

Now you can run examples directly:
```bash
python examples/01_chip_info.py 10.200.0.176
```

### For ESP32 MicroPython

1. Upload the `tropicsquare/` directory to your ESP32
2. Copy the example file you want to use and rename it to `main.py`
3. Upload `main.py` to your ESP32
4. The example will run automatically on boot

Using `mpremote`:
```bash
# Upload library
mpremote cp -r tropicsquare :

# Upload example as main.py
mpremote cp examples/01_chip_info.py :main.py

# Reset to run
mpremote reset
```

## Quick Start

**New to PyTropicSquare? Start here:**

1. **Absolute Beginner**: Start with `01_chip_info.py` - reads chip info, no secure session required
2. **First Crypto Operation**: Try `02_hello_ping.py` - establishes secure session and tests encrypted communication
3. **Generate Random Data**: Try `03_random_numbers.py` - use the hardware TRNG

All examples include detailed comments explaining each step.

## Transport Configuration

All universal examples support three transport methods via commented sections in the code. Simply **uncomment the transport section you want to use**.

### Option 1: Network SPI Bridge (Default)

Works on both CPython and MicroPython. Requires [netbridge32](https://github.com/petrkr/netbridge32) running on a device connected to the TROPIC01 chip.

```python
from tropicsquare.transports.network import NetworkSpiTransport
transport = NetworkSpiTransport('10.200.0.176', 12345)
```

**Usage:**
```bash
python 01_chip_info.py 192.168.1.123 12345
python 01_chip_info.py 192.168.1.123 # default port 12345
python 01_chip_info.py               # default 127.0.0.1:12345
```

**Platform notes:**
- ✅ CPython - works with command-line arguments
- ✅ Unix MicroPython - works with command-line arguments
- ⚠️  ESP32 MicroPython - `sys.argv` not available, examples use try/except fallback to defaults

### Option 2: Direct SPI (MicroPython Only)

Direct hardware connection via `machine.SPI`. Fastest option for production ESP32 deployments.

```python
from machine import SPI, Pin
from tropicsquare.transports.spi import SpiTransport

# ESP32 example - adjust pins for your hardware
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
         sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5, Pin.OUT)
transport = SpiTransport(spi, cs)
```

**Platform support:**
- ⚠️  **CPython (Raspberry Pi)** - TODO: `spidev` support not yet implemented (TROPIC01 Raspberry Pi shield available)
- ✅ **MicroPython ESP32** - via `machine.SPI`
- ❌ **MicroPython Unix** - no `machine.SPI` module available

### Option 3: UART SPI Bridge

Serial port bridge that translates UART commands to SPI. Works on CPython and Unix MicroPython.

```python
from tropicsquare.transports.uart import UartTransport
transport = UartTransport('/dev/ttyACM0', baudrate=115200)
```

**Platform support:**
- ✅ CPython (requires `pyserial`)
- ✅ Unix MicroPython (raw file I/O with termios)
- ❌ ESP32 MicroPython - **Physical limitation**: The USB UART dongle is a UART↔SPI bridge device itself, it cannot be connected to ESP32

**How to switch transports:**
1. Open the example file in a text editor
2. Find the `TRANSPORT CONFIGURATION` section
3. Comment out the default transport (Option 1)
4. Uncomment your preferred transport (Option 2 or 3)
5. Adjust parameters (pins, ports, addresses) as needed

## Examples by Category

### Getting Started (No crypto knowledge required)

| Example | Description | Requires Session |
|---------|-------------|------------------|
| **01_chip_info.py** | Read chip information, FW versions, certificate | No |
| **02_hello_ping.py** | Your first secure session and encrypted ping | Yes |
| **03_random_numbers.py** | Generate cryptographic random bytes | Yes |

### Cryptographic Operations (Coming Soon)

| Example | Description |
|---------|-------------|
| **10_ecc_key_management.py** | Generate, read, and erase ECC keys (P256, Ed25519) |
| **11_ecdsa_signing.py** | Sign data with ECDSA (P256 curve) |
| **12_eddsa_signing.py** | Sign data with EdDSA (Ed25519 curve) |
| **13_key_storage.py** | Import external keys into the chip |

### Data Storage (Coming Soon)

| Example | Description |
|---------|-------------|
| **20_memory_slots.py** | Store and retrieve secure data (up to 444 bytes per slot) |
| **21_monotonic_counters.py** | Anti-rollback counters |

### Configuration Management - Advanced (Coming Soon)

| Example | Description |
|---------|-------------|
| **30_config_basics.py** | Read R-CONFIG and I-CONFIG registers |
| **31_uap_permissions.py** | Understand User Access Policies |
| **32_effective_config.py** | R-CONFIG vs I-CONFIG behavior |

### Platform-Specific Examples (Coming Soon)

| Example | Platform | Description |
|---------|----------|-------------|
| **esp32_quickstart.py** | ESP32 MicroPython | Copy-paste ready example with direct SPI |
| **raspberry_pi_example.py** | Raspberry Pi (CPython) | Using UART or SPI on Raspberry Pi |
| **network_bridge_example.py** | Universal | Remote hardware via network bridge |

### Advanced Features (Coming Soon)

| Example | Description |
|---------|-------------|
| **40_mac_and_destroy.py** | Secure data destruction with MAC authentication |
| **41_complete_workflow.py** | Real-world application integration pattern |

## Platform Compatibility

| Example | CPython | MicroPython Unix | ESP32 MicroPython | Notes |
|---------|---------|------------------|-------------------|-------|
| 01-03 (Getting Started) | ✅ | ✅ | ✅ | Universal |
| 10-13 (Crypto) | ✅ | ✅ | ✅ | Coming soon |
| 20-21 (Storage) | ✅ | ✅ | ✅ | Coming soon |
| 30-32 (Config) | ✅ | ✅ | ✅ | Coming soon |
| esp32_quickstart.py | ❌ | ❌ | ✅ | ESP32 only |
| raspberry_pi_example.py | ✅ | ✅ | ❌ | Linux only |
| network_bridge_example.py | ✅ | ✅ | ✅ | Universal |
| 40-41 (Advanced) | ✅ | ✅ | ✅ | Coming soon |

### Platform-Specific Limitations

**sys.argv (Command-line arguments):**
- ✅ CPython - full support
- ✅ Unix MicroPython - full support
- ❌ ESP32 MicroPython - not available (examples use try/except fallback to hardcoded defaults)

**UartTransport:**
- ✅ CPython - uses `pyserial` library
- ✅ Unix MicroPython - raw file I/O with termios
- ❌ ESP32 MicroPython - physical limitation (UART dongle is already a UART↔SPI bridge)

**NetworkSpiTransport:**
- ✅ All platforms - universal compatibility

**SpiTransport:**
- ⚠️  CPython (Raspberry Pi) - TODO: `spidev` support not yet implemented
- ✅ MicroPython ESP32 - via `machine.SPI`
- ❌ MicroPython Unix - no `machine.SPI` module

## Pairing Keys

Examples use factory pairing keys from `tropicsquare.constants.pairing_keys`:

```python
from tropicsquare.constants.pairing_keys import *

# Factory key slot 0
FACTORY_PAIRING_KEY_INDEX = 0x00

# Production pairing keys (PROD0)
FACTORY_PAIRING_PRIVATE_KEY_PROD0  # 32 bytes
FACTORY_PAIRING_PUBLIC_KEY_PROD0   # 32 bytes

# Engineering sample keys (alternative)
FACTORY_PAIRING_PRIVATE_KEY_ENG_SAMPLE
FACTORY_PAIRING_PUBLIC_KEY_ENG_SAMPLE
```

## Error Handling Pattern

All examples follow this standard error handling pattern:

```python
def main():
    ts = TropicSquare(transport)

    try:
        # Operations here
        ts.start_secure_session(...)
        # ... do work ...
        ts.abort_secure_session()

    except TropicSquareAlarmError as e:
        print(f"ALARM: Chip is in alarm state: {e}")
        return 1
    except TropicSquareHandshakeError as e:
        print(f"HANDSHAKE ERROR: {e}")
        return 1
    except TropicSquareTimeoutError as e:
        print(f"TIMEOUT: {e}")
        return 1
    except TropicSquareCRCError as e:
        print(f"CRC ERROR: {e}")
        return 1
    except TropicSquareError as e:
        print(f"TROPICSQUARE ERROR: {e}")
        return 1
    finally:
        # Always clean up, even on error
        try:
            ts.abort_secure_session()
        except:
            pass

    return 0

if __name__ == "__main__":
    exit(main())
```

**Key points:**
- Session cleanup in `finally` block ensures sessions are always terminated
- Specific exception types for better error diagnosis
- Return codes for shell integration (0 = success, 1 = error)

## Learning Path

**Recommended progression for learning PyTropicSquare:**

### Beginner Track
1. `01_chip_info.py` - Understand basic chip communication
2. `02_hello_ping.py` - Learn secure sessions
3. `03_random_numbers.py` - Use hardware TRNG

### Cryptography Track
4. `10_ecc_key_management.py` - Key lifecycle management
5. `11_ecdsa_signing.py` - P256 digital signatures
6. `12_eddsa_signing.py` - Ed25519 signatures
7. `13_key_storage.py` - External key import

### Data Storage Track
8. `20_memory_slots.py` - Secure data storage
9. `21_monotonic_counters.py` - Anti-rollback protection

### Advanced Track
10. `30_config_basics.py` - Configuration registers
11. `31_uap_permissions.py` - Security policies
12. `32_effective_config.py` - R-CONFIG vs I-CONFIG
13. `40_mac_and_destroy.py` - Authenticated destruction
14. `41_complete_workflow.py` - Real-world integration

## Hardware Requirements

### Minimum Setup
- **TROPIC01 secure element chip**
- **One of the following:**
  - ESP32 with direct SPI connection (MicroPython)
  - Computer with network access to netbridge32 device
  - Raspberry Pi or Linux system with UART SPI bridge
  - Unix system with direct SPI hardware support

### Common Hardware Configurations

**ESP32 Development (Direct SPI):**
- ESP32 development board
- TROPIC01 evaluation board or breakout
- Wiring: SPI pins (SCK, MOSI, MISO, CS)
- Power supply (3.3V)

**Network Bridge Setup:**
- Computer running the examples (any platform)
- Device running [netbridge32](https://github.com/petrkr/netbridge32) (ESP32, etc.)
- TROPIC01 connected to bridge device via SPI
- Network connection between computer and bridge

**Raspberry Pi (UART Bridge):**
- Raspberry Pi (any model with GPIO)
- UART SPI bridge USB dongle
- TROPIC01 evaluation board
- USB cable

**Raspberry Pi (Direct SPI):**
- Raspberry Pi with SPI enabled
- TROPIC01 connected to Pi GPIO SPI pins
- Requires kernel SPI drivers and permissions

## Troubleshooting

### ModuleNotFoundError: No module named 'tropicsquare'

**Solution 1 (Recommended for development):**
```bash
pip install -e .
```

**Solution 2 (Quick test):**
```bash
PYTHONPATH=. python examples/01_chip_info.py
```

### Connection timeout or CRC errors

- Check wiring (especially on direct SPI connections)
- Verify network bridge is running and accessible
- Check SPI clock speed (try lower baudrate)
- Ensure chip has proper power supply (3.3V, stable)

### Handshake errors

- Verify you're using the correct pairing keys for your chip
- Check if chip is in alarm state (power cycle may help)
- Ensure no other process is communicating with the chip

### ESP32 sys.argv not working

- Expected behavior on ESP32 MicroPython
- Examples use try/except fallback to defaults
- Modify hardcoded values in the example file for your setup

## Support

- **Documentation:** [https://petrkr.github.io/pytropicsquare/](https://petrkr.github.io/pytropicsquare/)
- **Issues:** [https://github.com/petrkr/pytropicsquare/issues](https://github.com/petrkr/pytropicsquare/issues)
- **Main README:** [../README.md](../README.md)

## Contributing Examples

Have a useful example to share? Contributions are welcome!

**Guidelines for new examples:**
1. Follow the standard template (see existing examples)
2. Include comprehensive docstrings
3. Add transport configuration section with all three options
4. Implement proper error handling
5. Add cleanup in `finally` block
6. Test on both CPython and MicroPython if universal
7. Update this README with your example

## License

All examples are provided under the same license as PyTropicSquare (MIT License).
