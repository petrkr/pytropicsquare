#!/usr/bin/env python3
"""Example 01: Read Chip Information

This is the simplest example demonstrating basic chip communication.
It reads chip identification and firmware version information without
requiring a secure session.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 01_chip_info.py [host] [port]
    micropython 01_chip_info.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 01_chip_info.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 01_chip_info.py [port]
"""

from tropicsquare import TropicSquare
from tropicsquare.exceptions import *

# ==============================================================================
# TRANSPORT CONFIGURATION - Uncomment ONE section below
# ==============================================================================

# --- OPTION 1: Network SPI Bridge (default, CPython + MicroPython) ---
from tropicsquare.transports.network import NetworkSpiTransport

# Note: sys.argv works in CPython and Unix MicroPython, NOT in ESP32 MicroPython
# For ESP32, hardcode values or use different config method
try:
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
except:
    # ESP32 MicroPython fallback
    host = '127.0.0.1'
    port = 12345

transport = NetworkSpiTransport(host, port)
print(f"Using Network SPI bridge at {host}:{port}")

# --- OPTION 2: Direct SPI (MicroPython only - uncomment to use) ---
# from machine import SPI, Pin
# from tropicsquare.transports.spi import SpiTransport
#
# # ESP32 example pins - adjust for your hardware
# spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
#          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
# cs = Pin(5, Pin.OUT)
# transport = SpiTransport(spi, cs)
# print("Using direct SPI connection")

# --- OPTION 3: UART SPI Bridge (CPython + Unix MicroPython only, NOT ESP32) ---
# from tropicsquare.transports.uart import UartTransport
#
# # Note: UART bridge won't work on ESP32 MicroPython (physical limitation)
# # The USB dongle is a UART<->SPI bridge, can't be connected to ESP32
# try:
#     import sys
#     port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
# except:
#     port = '/dev/ttyACM0'
#
# transport = UartTransport(port, baudrate=115200)
# print(f"Using UART SPI bridge at {port}")

# ==============================================================================
# MAIN EXAMPLE CODE
# ==============================================================================

def main():
    """Read chip information without secure session.

    :returns: 0 on success, 1 on error
    :rtype: int
    """
    ts = TropicSquare(transport)

    try:
        print("\n=== CHIP IDENTIFICATION ===")
        print(ts.chipid)

        print("\n=== FIRMWARE VERSIONS ===")
        print(f"SPECT FW:  {ts.spect_fw_version}")
        print(f"RISC-V FW: {ts.riscv_fw_version}")

        print("\n=== CERTIFICATE ===")
        certificate = ts.certificate
        print(f"Length: {len(certificate)} bytes")
        print(f"Hex: {certificate.hex()}")

        print("\n=== PUBLIC KEY ===")
        public_key = ts.public_key
        print(f"Length: {len(public_key)} bytes")
        print(f"Hex: {public_key.hex()}")

        print("\n✓ Success!")
        return 0

    except TropicSquareAlarmError as e:
        print(f"\nALARM: Chip is in alarm state: {e}")
        return 1
    except TropicSquareHandshakeError as e:
        print(f"\nHANDSHAKE ERROR: {e}")
        return 1
    except TropicSquareTimeoutError as e:
        print(f"\nTIMEOUT: {e}")
        return 1
    except TropicSquareCRCError as e:
        print(f"\nCRC ERROR: {e}")
        return 1
    except TropicSquareError as e:
        print(f"\nTROPICSQUARE ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
