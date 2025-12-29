#!/usr/bin/env micropython
"""ESP32 Quick Start - Direct SPI Connection

This is a platform-specific example for ESP32 MicroPython showing direct
hardware SPI connection to the TROPIC01 chip. Perfect for ESP32-based
production deployments.

Features demonstrated:
- Direct ESP32 SPI communication via machine.SPI
- Basic chip information retrieval
- Secure session establishment
- Encrypted ping test
- Device log retrieval

Hardware Requirements:
- ESP32 development board
- TROPIC01 chip or evaluation board
- SPI connections (SCK, MOSI, MISO, CS)
- 3.3V power supply

Usage:
    1. Upload the tropicsquare/ library to your ESP32:
       mpremote cp -r tropicsquare :

    2. Copy this file as main.py and upload:
       mpremote cp examples/esp32_quickstart.py :main.py

    3. Reset your ESP32:
       mpremote reset

    The example will run automatically on boot.

Pin Configuration:
    Adjust the pin definitions below to match your hardware setup.
"""

from machine import SPI, Pin

from tropicsquare import TropicSquare
from tropicsquare.transports.spi import SpiTransport
from tropicsquare.constants.pairing_keys import *
from tropicsquare.exceptions import *

# ==============================================================================
# ESP32 HARDWARE CONFIGURATION - Adjust for your hardware
# ==============================================================================
SPI_BUS = 1
SPI_BAUDRATE = 1_000_000
PIN_SCK = 18
PIN_MOSI = 23
PIN_MISO = 19
PIN_CS = 5


def main():
    """ESP32 quick start example with direct SPI connection.

    :returns: 0 on success, 1 on error
    :rtype: int
    """
    # Initialize SPI hardware
    spi = SPI(SPI_BUS, baudrate=SPI_BAUDRATE, polarity=0, phase=0,
              sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI), miso=Pin(PIN_MISO))
    cs = Pin(PIN_CS, Pin.OUT)

    ts = TropicSquare(SpiTransport(spi, cs))

    try:
        print("\n=== CHIP INFORMATION ===")
        print(f"SPECT FW:  {ts.spect_fw_version}")
        print(f"RISC-V FW: {ts.riscv_fw_version}")
        print(f"Chip ID:   {ts.chipid.hex()}")
        print(f"Cert Pub:  {ts.public_key.hex()}")

        print("\n=== STARTING SECURE SESSION ===")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        print("✓ Session established")

        print("\n=== PING TEST ===")
        message = b"Hello TROPIC01 from ESP32!"
        print(f"Sending:  {message.decode()}")
        response = ts.ping(message)
        print(f"Response: {response.decode()}")
        print(f"✓ Ping {'successful' if response == message else 'failed'}")

        print("\n=== DEVICE LOG ===")
        print(ts.get_log())

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
