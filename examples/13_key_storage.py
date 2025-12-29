#!/usr/bin/env python3
"""Example 13: Import External Keys

This example demonstrates how to import externally generated ECC keys into
the TROPIC01's secure key slots using the key storage function.

It shows:
- Importing a private key into a secure slot
- Retrieving the corresponding public key
- Verifying the imported key
- Understanding key import security considerations

⚠️  SECURITY WARNING ⚠️
    This example uses a DEMO private key for illustration purposes ONLY.
    In production:
    - Generate keys using cryptographically secure methods
    - Never hardcode private keys in source code
    - Use secure key derivation or import from hardware security modules
    - Protect private key material during transport and storage

The example uses slot 2, which is not used by the other examples.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 13_key_storage.py [host] [port]
    micropython 13_key_storage.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 13_key_storage.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 13_key_storage.py [port]
"""

from tropicsquare import TropicSquare
from tropicsquare.constants import ECC_CURVE_P256, ECC_CURVE_ED25519
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
    """Import external ECC key into secure slot.

    :returns: 0 on success, 1 on error
    :rtype: int
    """
    ts = TropicSquare(transport)

    try:
        print("\n" + "=" * 70)
        print("  ⚠️  SECURITY WARNING ⚠️")
        print("=" * 70)
        print("This example uses a DEMO private key for illustration ONLY.")
        print("NEVER use this key in production!")
        print("\nIn production:")
        print("  • Generate keys using cryptographically secure methods")
        print("  • Never hardcode private keys in source code")
        print("  • Use secure key derivation or HSM import")
        print("=" * 70)

        print("\n=== STARTING SECURE SESSION ===")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        print("✓ Session established")

        # ======================================================================
        # PREPARE DEMO PRIVATE KEY
        # ======================================================================
        print("\n=== PREPARING DEMO PRIVATE KEY ===")

        # WARNING: This is a DEMO key only! Never use in production!
        # Real P256 private key should be 32 bytes of cryptographically secure random data
        demo_private_key = bytes.fromhex("1234567890abcdef" * 4)

        print(f"Demo private key: {demo_private_key.hex()}")
        print(f"Key size:         {len(demo_private_key)} bytes")
        print(f"Curve:            P256")
        print(f"Target slot:      2")

        # ======================================================================
        # CHECK IF SLOT IS EMPTY
        # ======================================================================
        print("\n=== CHECKING SLOT 2 ===")
        try:
            curve, origin, existing_pubkey = ts.ecc_key_read(2)

            # Determine curve name
            if curve == ECC_CURVE_P256:
                curve_name = "P256"
            elif curve == ECC_CURVE_ED25519:
                curve_name = "Ed25519"
            else:
                curve_name = f"Unknown (0x{curve:02x})"

            print(f"⚠ WARNING: Slot 2 already contains a key")
            print(f"  Curve:      {curve_name}")
            print(f"  Public key: {existing_pubkey.hex()}")
            print("\nTo import a new key, first erase the existing one:")
            print("  ts.ecc_key_erase(2)")
            print("\nSkipping import to preserve existing key.")
            return 1
        except TropicSquareError:
            print("✓ Slot 2 is empty, proceeding with import")

        # ======================================================================
        # IMPORT KEY INTO SLOT 2
        # ======================================================================
        print("\n=== IMPORTING KEY INTO SLOT 2 ===")
        print("Storing private key...")

        result = ts.ecc_key_store(2, ECC_CURVE_P256, demo_private_key)

        if not result:
            print("❌ ERROR: Key storage failed")
            return 1

        print(f"✓ Key stored successfully")

        # Read back the public key
        _, _, public_key = ts.ecc_key_read(2)
        print(f"  Public key: {public_key.hex()}")
        print(f"  Public key size: {len(public_key)} bytes")

        # ======================================================================
        # VERIFY IMPORT
        # ======================================================================
        print("\n=== VERIFYING IMPORT ===")
        print("Reading slot 2 again to confirm storage...")

        _, curve_read, pubkey_verify = ts.ecc_key_read(2)

        print(f"✓ Key verified in slot 2")
        print(f"  Curve:      {curve_read} (P256)")
        print(f"  Public key: {pubkey_verify.hex()}")
        print(f"  Match:      {public_key == pubkey_verify}")

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print("\n=== IMPORT SUCCESSFUL ===")
        print("✓ External P256 key successfully imported to slot 2")
        print("\nThe imported key can now be used for:")
        print("  • ECDSA signing (like in 11_ecdsa_signing.py)")
        print("  • Other cryptographic operations")
        print("\nKey remains in slot 2 until explicitly erased:")
        print("  ts.ecc_key_erase(2)")

        print("\n=== PRODUCTION KEY IMPORT ===")
        print("In production, import keys from secure sources:")
        print("  • Hardware Security Modules (HSM)")
        print("  • Secure key generation libraries:")
        print("    - Python: cryptography.hazmat.primitives.asymmetric.ec")
        print("    - secrets module for random generation")
        print("  • Derived from secure entropy sources")

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
