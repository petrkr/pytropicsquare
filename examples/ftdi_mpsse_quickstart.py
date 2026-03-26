"""Example: Using FTDI MPSSE Transport with FT2232H/FT2232HL

Prerequisites:
    - Python package: pyftdi
    - FTDI MPSSE-capable device (tested with FT2232HL)

Hardware:
    AD0 -> SCK
    AD1 -> MOSI
    AD2 -> MISO
    AD3 -> CS
    GND -> GND

Notes:
    - Uses FTDI channel A by default: ftdi://ftdi:2232h/1
    - Uses FTDI native SPI /CS on AD3

Usage:
    python examples/ftdi_mpsse_quickstart.py
"""

import sys

from pyftdi.spi import SpiController

from tropicsquare import TropicSquare
from tropicsquare.transports.ftdi_mpsse import FtdiMpsseTransport
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0,
)


FTDI_URL = "ftdi://ftdi:2232h/1"
SPI_FREQUENCY = 1_000_000


def main():
    print("Initializing TROPIC01 via FTDI MPSSE...")
    print(f"Hardware: {FTDI_URL}, AD3 for CS (native SPI control)")

    controller = SpiController(cs_count=1)
    controller.configure(FTDI_URL)
    spi = controller.get_port(cs=0, freq=SPI_FREQUENCY, mode=0)
    transport = FtdiMpsseTransport(spi)

    try:
        ts = TropicSquare(transport)

        print("Connected successfully!")

        print("\n=== Chip Information ===")
        print(ts.chip_id)
        print(f"RISCV FW Version: {'.'.join(map(str, ts.riscv_fw_version))}")
        print(f"SPECT FW Version: {'.'.join(map(str, ts.spect_fw_version))}")

        print("\n=== Starting Secure Session ===")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0,
        )
        print("Secure session established!")

        print("\n=== Testing Ping Command ===")
        test_data = b"Hello TROPIC01 from FTDI!"
        print(f"Sending: {test_data}")
        response = ts.ping(test_data)
        print(f"Response: {response}")

        if response == test_data:
            print("Ping test PASSED!")
        else:
            print("Ping test FAILED!")

        print("\n=== Testing Random Generation ===")
        random_data = ts.random(16)
        print(f"Random data (16 bytes): {random_data.hex()}")

        random_data = ts.random(32)
        print(f"Random data (32 bytes): {random_data.hex()}")

        print("\n=== Test Complete ===")
        print("All operations successful!")

    finally:
        print("\nCleaning up...")
        controller.close()
        print("Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
