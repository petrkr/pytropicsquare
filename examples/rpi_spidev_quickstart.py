"""Example: Using SPIDev Transport on Raspberry Pi

Prerequisites:
    - Python packages: pip install spidev gpiod
    - User permissions: sudo usermod -a -G spi,gpio $USER (then re-login)
    - Device tree overlay (ONLY if you have other devices on CE0/CE1):
      Add to /boot/firmware/config.txt: dtoverlay=spi0-0cs
      See SpiDevTransport docstring for details.

Hardware:
    SPI0: MISO=GPIO9, MOSI=GPIO10, SCK=GPIO11
    CS: GPIO 25 (physical pin 22) - or any free GPIO

Usage:
    python examples/rpi_spidev_quickstart.py
"""

import sys
from tropicsquare import TropicSquare
from tropicsquare.transports.spidev import SpiDevTransport
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)


def main():
    # Use any free GPIO for CS (e.g., GPIO 25)
    # dtoverlay=spi0-0cs only needed if you have other devices on CE0/CE1
    cs_pin = 25         # GPIO 25 (physical pin 22)

    print("Initializing TROPIC01 via SPIDev on Raspberry Pi...")
    print(f"Hardware: SPI0, GPIO {cs_pin} for CS (manual control)")

    # Create SPIDev transport
    transport = SpiDevTransport(
        bus=0,
        device=0,
        cs_pin=cs_pin,
        max_speed_hz=1000000
    )

    try:
        # Create TropicSquare instance
        ts = TropicSquare(transport)

        print("Connected successfully!")

        # Get chip information
        print("\n=== Chip Information ===")
        print(ts.chipid)
        print(f"RISCV FW Version: {'.'.join(map(str, ts.riscv_fw_version))}")
        print(f"SPECT FW Version: {'.'.join(map(str, ts.spect_fw_version))}")

        # Start secure session
        print("\n=== Starting Secure Session ===")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        print("Secure session established!")

        # Test ping command
        print("\n=== Testing Ping Command ===")
        test_data = b"Hello TROPIC01 from RPi!"
        print(f"Sending: {test_data}")
        response = ts.ping(test_data)
        print(f"Response: {response}")

        if response == test_data:
            print("✓ Ping test PASSED!")
        else:
            print("✗ Ping test FAILED!")

        # Generate random data
        print("\n=== Testing Random Generation ===")
        random_data = ts.get_random(16)
        print(f"Random data (16 bytes): {random_data.hex()}")

        # Get another batch
        random_data = ts.get_random(32)
        print(f"Random data (32 bytes): {random_data.hex()}")

        print("\n=== Test Complete ===")
        print("All operations successful!")

    finally:
        # Always cleanup hardware resources
        print("\nCleaning up...")
        transport.close()
        print("Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except PermissionError as e:
        print(f"\nPermission Error: {e}")
        print("\nMake sure you have permissions for /dev/spidev0.0 and /dev/gpiochip0")
        print("Add your user to required groups:")
        print("  sudo usermod -a -G spi,gpio $USER")
        print("Then log out and back in.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
