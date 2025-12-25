#!/usr/bin/env python3
"""
NetworkUART-SPI Test Script

This script tests the NetworkUART-SPI client by connecting to a remote
NetworkUART-SPI server that bridges to a UART-SPI device.

Usage:
    python testNETUART.py [host] [port]

Arguments:
    host    Server hostname or IP address (default: localhost)
    port    Server TCP port (default: 12345)

Example:
    python testNETUART.py 192.168.1.100 12345
"""

import sys

from tropicsquare import TropicSquare
from tropicsquare.exceptions import *
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)
from tropicsquare.transports.network import NetworkSpiTransport


def main():
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 12345

    print(f"Connecting to NetworkUART-SPI server at {host}:{port}...")

    # L1 layer - Network UART-SPI

    print("Connected! Initializing TropicSquare...")
    ts = TropicSquare(NetworkSpiTransport(host, port))

    try:
        # Get chip information (outside session)
        print("=" * 60)
        print("CHIP IDENTIFICATION")
        print("=" * 60)
        chip_id = ts.chipid
        print(chip_id)  # Human-readable output
        print("\nRaw Chip ID: {}".format(chip_id.raw.hex()))
        print("\nSpect FW version: {}".format(ts.spect_fw_version))
        print("RISCV FW version: {}".format(ts.riscv_fw_version))

        try:
            print("FW Bank: {}".format(ts.fw_bank))
        except TropicSquareError as e:
            print("FW Bank unavailable: {}".format(e))

        print("\n" + "=" * 60)
        print("CERTIFICATE")
        print("=" * 60)
        print("RAW Certificate: {}".format(ts.certificate.hex()))
        print("Cert Public Key: {}".format(ts.public_key.hex()))

        # Test ChipId dict export
        print("\n" + "=" * 60)
        print("CHIP ID DETAILS (dict export)")
        print("=" * 60)
        chip_id_dict = chip_id.to_dict()
        for key, value in chip_id_dict.items():
            if key == 'serial_number':
                print(f"  {key}:")
                for sn_key, sn_value in value.items():
                    print(f"    {sn_key}: {sn_value}")
            else:
                print(f"  {key}: {value}")

        print("\nStarting secure session...")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        print("Secure session established!")

        # Test ping with long message (chunk required)
        print("\n" + "=" * 60)
        print("TESTING PING")
        print("=" * 60)
        resp = ts.ping(b"Very long ping! Chunk required..." * 5)
        print("Ping response: {}".format(resp))

        # Test ECC key operations
        print("\n" + "=" * 60)
        print("TESTING ECC KEY OPERATIONS")
        print("=" * 60)
        try:
            print("ECC Pubkey #0: {}".format(ts.ecc_key_read(0)[2].hex()))
            print("ECC Pubkey #1: {}".format(ts.ecc_key_read(1)[2].hex()))
        except TropicSquareECCError as e:
            print("ECC key read error: {}".format(e))

        # Test signing operations
        print("\n" + "=" * 60)
        print("TESTING SIGNING OPERATIONS")
        print("=" * 60)
        try:
            sign = ts.eddsa_sign(0, b"Hello Tropic Square From Network UART!")
            print("EdDSA signature by key #0:")
            print("  R: {}".format(sign[0].hex()))
            print("  S: {}".format(sign[1].hex()))
        except TropicSquareECCError as e:
            print("EdDSA signing error: {}".format(e))

        # Test ECDSA with SHA256 of "Ahoj"
        try:
            sign = ts.ecdsa_sign(
                1,
                b'\xd2z\x7f\x03\x8bq^\x0b\x8aC\x8a\tpN1\x02\x15\nAX\xa7\xf17+\xb6\xe0\xe6X\xc0\x0e|\n'
            )
            print("ECDSA signature by key #1:")
            print("  R: {}".format(sign[0].hex()))
            print("  S: {}".format(sign[1].hex()))
        except TropicSquareECCError as e:
            print("ECDSA signing error: {}".format(e))

        # Test monotonic counter
        print("\n" + "=" * 60)
        print("TESTING MONOTONIC COUNTER")
        print("=" * 60)
        print("Initializing monotonic counter #0 with value 3")
        ts.mcounter_init(0, 3)
        print("Counter value: {}".format(ts.mcounter_get(0)))

        print("Updating monotonic counter")
        ts.mcounter_update(0)
        print("Counter value after update: {}".format(ts.mcounter_get(0)))

        # Test random number generation
        print("\n" + "=" * 60)
        print("TESTING RANDOM NUMBER GENERATION")
        print("=" * 60)
        try:
            for i in range(4):
                random = ts.get_random(4)
                print("Random #{}: {}".format(i + 1, random.hex()))
        except TropicSquareError as e:
            print("Random generation error: {}".format(e))

        # Get device log
        print("\n" + "=" * 60)
        print("DEVICE LOG")
        print("=" * 60)
        print(ts.get_log())

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except TropicSquareAlarmError as e:
        print("ALARM: Chip is in alarm state: {}".format(e))
    except TropicSquareHandshakeError as e:
        print("HANDSHAKE ERROR: {}".format(e))
    except TropicSquareTimeoutError as e:
        print("TIMEOUT: {}".format(e))
    except TropicSquareCRCError as e:
        print("CRC ERROR: {}".format(e))
    except TropicSquareError as e:
        print("TROPICSQUARE ERROR: {}".format(e))
    except Exception as e:
        print("UNEXPECTED ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
    finally:
        # Clean up connection
        print("\nClosing connection...")


if __name__ == "__main__":
    main()
