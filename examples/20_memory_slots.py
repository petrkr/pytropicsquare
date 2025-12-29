#!/usr/bin/env python3
"""Example 20: Secure Memory Slots

This example demonstrates how to use the TROPIC01's secure memory slots for
storing encrypted data in the chip's protected memory.

It shows:
- Checking if a memory slot contains data
- Writing data to memory slots (up to 444 bytes)
- Reading data back from memory slots
- Understanding memory slot security and usage

Memory slots provide secure storage for:
- Configuration data
- Credentials and tokens
- Application-specific persistent data
- Small encrypted payloads

Data is stored encrypted and protected by the chip's security features.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 20_memory_slots.py [host] [port]
    micropython 20_memory_slots.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 20_memory_slots.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 20_memory_slots.py [port]
"""

from tropicsquare import TropicSquare
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

# Configuration
MEMORY_SLOT = 0
MAX_DATA_SIZE = 444  # Maximum bytes per slot

def main():
    """Demonstrate secure memory slot operations.

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
        # CHECK IF SLOT CONTAINS DATA
        # ======================================================================
        print(f"\n=== CHECKING MEMORY SLOT {MEMORY_SLOT} ===")
        slot_has_data = False
        existing_data = None

        try:
            existing_data = ts.mem_data_read(MEMORY_SLOT)
            if existing_data and len(existing_data) > 0:
                slot_has_data = True
                print(f"⚠ WARNING: Slot {MEMORY_SLOT} already contains data")
                print(f"  Data size: {len(existing_data)} bytes")
                print(f"  Data (hex): {existing_data.hex()[:80]}{'...' if len(existing_data.hex()) > 80 else ''}")

                # Try to decode as text if possible
                try:
                    text = existing_data.decode('utf-8')
                    print(f"  Data (text): {text[:60]}{'...' if len(text) > 60 else ''}")
                except:
                    print(f"  Data (text): <binary data>")

                print("\nTo write new data, first erase the existing data:")
                print(f"  ts.mem_data_erase({MEMORY_SLOT})")
                print("\nSkipping write to preserve existing data.")
            else:
                print(f"✓ Slot {MEMORY_SLOT} is empty")
        except TropicSquareError:
            print(f"✓ Slot {MEMORY_SLOT} is empty")

        # ======================================================================
        # WRITE DATA (if slot is empty)
        # ======================================================================
        if not slot_has_data:
            print(f"\n=== WRITING DATA TO SLOT {MEMORY_SLOT} ===")

            # Prepare demo data
            demo_data = b"Hello from TROPIC01! Secure storage example."
            print(f"Data to write: {demo_data.decode()}")
            print(f"Data size:     {len(demo_data)} bytes (max: {MAX_DATA_SIZE})")

            # Write to slot
            ts.mem_data_write(demo_data, MEMORY_SLOT)
            print(f"✓ Data written successfully to slot {MEMORY_SLOT}")

            # ======================================================================
            # READ DATA BACK
            # ======================================================================
            print(f"\n=== READING DATA FROM SLOT {MEMORY_SLOT} ===")
            read_data = ts.mem_data_read(MEMORY_SLOT)

            print(f"Read {len(read_data)} bytes")
            print(f"Data (hex):  {read_data.hex()}")
            print(f"Data (text): {read_data.decode()}")

            # Verify data integrity
            if read_data == demo_data:
                print(f"✓ Data integrity verified - read data matches written data")
            else:
                print(f"❌ ERROR: Data mismatch!")
                return 1

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print(f"\n=== SUMMARY ===")
        if slot_has_data:
            print(f"Slot {MEMORY_SLOT} contains existing data ({len(existing_data)} bytes)")
            print("No changes made to preserve existing data")
        else:
            print(f"✓ Successfully demonstrated memory slot operations")
            print(f"  • Written: 45 bytes")
            print(f"  • Read:    45 bytes")
            print(f"  • Verified: Data integrity OK")

        print(f"\n=== USE CASES ===")
        print("Memory slots are ideal for:")
        print("  • Configuration data storage")
        print("  • Credentials and API tokens")
        print("  • Application state persistence")
        print("  • Small encrypted payloads")
        print(f"\nCapacity: Up to {MAX_DATA_SIZE} bytes per slot")

        print(f"\n=== MEMORY MANAGEMENT ===")
        print(f"Data remains in slot {MEMORY_SLOT} until explicitly erased:")
        print(f"  ts.mem_data_erase({MEMORY_SLOT})")
        print("\nData is stored encrypted and protected by chip security.")

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
