#!/usr/bin/env python3
"""Example 12: EdDSA Signing with Ed25519

This example demonstrates how to create EdDSA (Edwards-curve Digital Signature
Algorithm) signatures using the TROPIC01's Ed25519 curve key.

It shows:
- Verifying that an Ed25519 key exists in the key slot
- Creating EdDSA signatures using hardware-protected keys
- Understanding the signature format (R, S components)
- The difference between EdDSA and ECDSA (EdDSA signs message directly)

Prerequisites:
    Run 10_ecc_key_management.py first to generate the Ed25519 key in slot 0.

Important Note:
    Unlike ECDSA, EdDSA signs the message *directly* without requiring
    pre-hashing. The chip performs all necessary operations internally.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 12_eddsa_signing.py [host] [port]
    micropython 12_eddsa_signing.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 12_eddsa_signing.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 12_eddsa_signing.py [port]
"""

from tropicsquare import TropicSquare
from tropicsquare.constants.ecc import ECC_CURVE_ED25519
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
    """Create EdDSA signature using Ed25519 key.

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
        # CHECK FOR Ed25519 KEY
        # ======================================================================
        print("\n=== CHECKING FOR Ed25519 KEY ===")
        try:
            key_info = ts.ecc_key_read(0)
            print(f"✓ Found Ed25519 key in slot 0")
            print(f"  Public key: {key_info.public_key.hex()}")
        except TropicSquareError as e:
            print(f"\n❌ ERROR: No Ed25519 key found in slot 0")
            print("Please run: python 10_ecc_key_management.py")
            print("\nThis will generate the required Ed25519 key.")
            return 1

        # ======================================================================
        # PREPARE MESSAGE
        # ======================================================================
        print("\n=== PREPARING MESSAGE ===")
        message = b"Hello TROPIC01!"

        print(f"Message:     {message.decode()}")
        print(f"Message size: {len(message)} bytes")
        print("\nNOTE: EdDSA signs the message directly (no pre-hashing needed)")

        # ======================================================================
        # CREATE EdDSA SIGNATURE
        # ======================================================================
        print("\n=== SIGNING WITH EdDSA (Ed25519) ===")
        signature = ts.eddsa_sign(0, message)

        print(f"Signature R: {signature.r.hex()}")
        print(f"Signature S: {signature.s.hex()}")
        print(f"R size:      {len(signature.r)} bytes")
        print(f"S size:      {len(signature.s)} bytes")

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print("\n=== SIGNATURE CREATED SUCCESSFULLY ===")
        print("✓ EdDSA signature generated using hardware-protected Ed25519 key")
        print("\nNOTE: This signature can be verified using:")
        print("  - The public key shown above")
        print("  - Standard Ed25519 verification (e.g., libsodium, cryptography library)")
        print("  - The original message")

        print("\n=== KEY DIFFERENCE: EdDSA vs ECDSA ===")
        print("EdDSA (this example):")
        print("  • Signs message directly")
        print("  • No pre-hashing required")
        print("  • Uses Ed25519 curve")
        print("\nECDSA (example 11_ecdsa_signing.py):")
        print("  • Signs hash of message (e.g., SHA256)")
        print("  • Requires pre-hashing")
        print("  • Uses P256 curve")

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
