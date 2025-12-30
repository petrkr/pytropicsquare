#!/usr/bin/env python3
"""Example 11: ECDSA Signing with P256

This example demonstrates how to create ECDSA (Elliptic Curve Digital Signature
Algorithm) signatures using the TROPIC01's P256 curve key.

It shows:
- Verifying that a P256 key exists in the key slot
- Computing SHA256 hash of a message
- Creating ECDSA signatures using hardware-protected keys
- Understanding the signature format (R, S components)

Prerequisites:
    Run 10_ecc_key_management.py first to generate the P256 key in slot 1.

Important Note:
    ECDSA signs the *hash* of the message, not the message itself.
    This example uses SHA256 for hashing.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 11_ecdsa_signing.py [host] [port]
    micropython 11_ecdsa_signing.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 11_ecdsa_signing.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 11_ecdsa_signing.py [port]
"""

import hashlib
from tropicsquare import TropicSquare
from tropicsquare.constants.ecc import ECC_CURVE_P256
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
    """Create ECDSA signature using P256 key.

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
        # CHECK FOR P256 KEY
        # ======================================================================
        print("\n=== CHECKING FOR P256 KEY ===")
        try:
            key_info = ts.ecc_key_read(1)
            print(f"✓ Found P256 key in slot 1")
            print(f"  Public key: {key_info.public_key.hex()}")
        except TropicSquareError as e:
            print(f"\n❌ ERROR: No P256 key found in slot 1")
            print("Please run: python 10_ecc_key_management.py")
            print("\nThis will generate the required P256 key.")
            return 1

        # ======================================================================
        # PREPARE MESSAGE AND HASH
        # ======================================================================
        print("\n=== COMPUTING MESSAGE HASH ===")
        message = b"Hello TROPIC01!"
        message_hash = hashlib.sha256(message).digest()

        print(f"Message:    {message.decode()}")
        print(f"SHA256:     {message_hash.hex()}")
        print(f"Hash size:  {len(message_hash)} bytes")

        # ======================================================================
        # CREATE ECDSA SIGNATURE
        # ======================================================================
        print("\n=== SIGNING WITH ECDSA (P256) ===")
        signature = ts.ecdsa_sign(1, message_hash)

        print(f"Signature R: {signature.r.hex()}")
        print(f"Signature S: {signature.s.hex()}")
        print(f"R size:      {len(signature.r)} bytes")
        print(f"S size:      {len(signature.s)} bytes")

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print("\n=== SIGNATURE CREATED SUCCESSFULLY ===")
        print("✓ ECDSA signature generated using hardware-protected P256 key")
        print("\nNOTE: This signature can be verified using:")
        print("  - The public key shown above")
        print("  - Standard ECDSA verification (e.g., OpenSSL, cryptography library)")
        print("  - The original message hash")

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
