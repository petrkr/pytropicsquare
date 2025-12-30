#!/usr/bin/env python3
"""Example 10: ECC Key Management

This example demonstrates how to generate and manage ECC keys in the
TROPIC01's secure key slots. It serves as a setup example for the signing
examples (11_ecdsa_signing.py and 12_eddsa_signing.py).

It shows:
- Checking if keys already exist in slots
- Generating Ed25519 keys (for EdDSA signatures)
- Generating P256 keys (for ECDSA signatures)
- Reading public keys from slots
- Non-destructive key management (keys persist for reuse)

The example generates keys in two slots:
- Slot 0: Ed25519 key (used by 12_eddsa_signing.py)
- Slot 1: P256 key (used by 11_ecdsa_signing.py)

Keys are left in the chip for use by signing examples. To erase keys,
see the cleanup instructions in the output.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 10_ecc_key_management.py [host] [port]
    micropython 10_ecc_key_management.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 10_ecc_key_management.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 10_ecc_key_management.py [port]
"""

from tropicsquare import TropicSquare
from tropicsquare.constants.ecc import ECC_CURVE_P256, ECC_CURVE_ED25519
from tropicsquare.constants.pairing_keys import *
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
    """Generate and manage ECC keys in secure key slots.

    :returns: 0 on success, 1 on error
    :rtype: int
    """
    ts = TropicSquare(transport)

    try:
        print("\n=== STARTING SECURE SESSION ===")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        print("✓ Session established")

        # ======================================================================
        # SLOT 0: Ed25519 Key (for EdDSA signing)
        # ======================================================================
        print("\n=== CHECKING SLOT 0 (Ed25519) ===")
        try:
            # Try to read existing key
            key_info = ts.ecc_key_read(0)
            print(f"✓ Key already exists in slot 0")
            print(f"  Public key: {key_info.public_key.hex()}")
        except TropicSquareError:
            # Slot is empty, generate new key
            print("Slot 0 is empty, generating Ed25519 key...")
            ts.ecc_key_generate(0, ECC_CURVE_ED25519)
            key_info = ts.ecc_key_read(0)
            print(f"✓ Ed25519 key generated successfully")
            print(f"  Public key: {key_info.public_key.hex()}")

        # ======================================================================
        # SLOT 1: P256 Key (for ECDSA signing)
        # ======================================================================
        print("\n=== CHECKING SLOT 1 (P256) ===")
        try:
            # Try to read existing key
            key_info = ts.ecc_key_read(1)
            print(f"✓ Key already exists in slot 1")
            print(f"  Public key: {key_info.public_key.hex()}")
        except TropicSquareError:
            # Slot is empty, generate new key
            print("Slot 1 is empty, generating P256 key...")
            ts.ecc_key_generate(1, ECC_CURVE_P256)
            key_info = ts.ecc_key_read(1)
            print(f"✓ P256 key generated successfully")
            print(f"  Public key: {key_info.public_key.hex()}")

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print("\n=== SUMMARY ===")
        print("✓ Keys are ready for signing examples:")
        print("  - Slot 0 (Ed25519): Use with 12_eddsa_signing.py")
        print("  - Slot 1 (P256):    Use with 11_ecdsa_signing.py")

        print("\n=== CLEANUP OPTIONS ===")
        print("Keys are left in chip for repeated use.")
        print("To erase keys manually:")
        print("  ts.ecc_key_erase(0)  # Erase Ed25519 key")
        print("  ts.ecc_key_erase(1)  # Erase P256 key")

        print("\n=== CLEANUP ===")
        ts.abort_secure_session()
        print("✓ Session terminated")

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
    finally:
        # Always try to clean up the session, even if an error occurred
        try:
            ts.abort_secure_session()
        except:
            pass


if __name__ == "__main__":
    main()
