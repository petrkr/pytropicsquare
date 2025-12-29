#!/usr/bin/env python3
"""Example 21: Monotonic Counters

This example demonstrates how to use the TROPIC01's monotonic counters for
anti-rollback protection and version tracking.

It shows:
- Checking if a counter already exists
- Initializing new monotonic counters
- Reading counter values
- Updating (incrementing) counters
- Understanding use cases for monotonic counters

Monotonic counters are useful for:
- Anti-rollback protection (firmware version tracking)
- Replay attack prevention
- Usage counting and rate limiting
- Ensuring operations occur in order

The counter only moves in one direction (up) and cannot be decremented,
making it suitable for security-critical applications.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 21_monotonic_counters.py [host] [port]
    micropython 21_monotonic_counters.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 21_monotonic_counters.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 21_monotonic_counters.py [port]
"""

from tropicsquare import TropicSquare
from tropicsquare.constants.pairing_keys import *
from tropicsquare.exceptions import (
    TropicSquareError,
    TropicSquareAlarmError,
    TropicSquareHandshakeError,
    TropicSquareTimeoutError,
    TropicSquareCRCError,
    TropicSquareCounterUpdateError,
)

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
COUNTER_INDEX = 0
INITIAL_VALUE = 100  # Starting value for new counters

def main():
    """Demonstrate monotonic counter operations.

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
        # CHECK IF COUNTER EXISTS
        # ======================================================================
        print(f"\n=== CHECKING COUNTER {COUNTER_INDEX} ===")
        counter_exists = False
        try:
            current_value = ts.mcounter_get(COUNTER_INDEX)
            counter_exists = True
            print(f"✓ Counter {COUNTER_INDEX} already exists")
            print(f"  Current value: {current_value}")
            print("\nSkipping initialization to preserve existing counter.")
        except TropicSquareError:
            print(f"✓ Counter {COUNTER_INDEX} is not initialized")

        # ======================================================================
        # INITIALIZE COUNTER (if not exists)
        # ======================================================================
        if not counter_exists:
            print(f"\n=== INITIALIZING COUNTER {COUNTER_INDEX} ===")
            print(f"Setting initial value to: {INITIAL_VALUE}")
            ts.mcounter_init(COUNTER_INDEX, INITIAL_VALUE)
            print(f"✓ Counter {COUNTER_INDEX} initialized successfully")

            # Read back to verify
            current_value = ts.mcounter_get(COUNTER_INDEX)
            print(f"  Verified value: {current_value}")

        # ======================================================================
        # UPDATE COUNTER
        # ======================================================================
        print(f"\n=== UPDATING COUNTER {COUNTER_INDEX} ===")
        print(f"Current value: {current_value}")
        print("\nNOTE: Monotonic counters DECREMENT (count down) from initial value")
        print("      When counter reaches 0, it cannot be decremented further")

        try:
            ts.mcounter_update(COUNTER_INDEX)
            new_value = ts.mcounter_get(COUNTER_INDEX)

            print(f"✓ Counter updated")
            print(f"  New value: {new_value}")
            print(f"  Change:    {current_value} → {new_value}")
        except TropicSquareCounterUpdateError as e:
            # Counter reached zero - cannot decrement further
            print(f"⚠ Counter exhausted (reached zero)")
            print(f"  {e}")
            new_value = 0

        # ======================================================================
        # DEMONSTRATE MULTIPLE UPDATES
        # ======================================================================
        print(f"\n=== MULTIPLE UPDATES ===")
        print("Attempting to update counter 3 more times...")

        updates_successful = 0
        for i in range(3):
            try:
                ts.mcounter_update(COUNTER_INDEX)
                value = ts.mcounter_get(COUNTER_INDEX)
                print(f"  Update {i+1}: {value}")
                updates_successful += 1
            except TropicSquareCounterUpdateError as e:
                print(f"  Update {i+1}: ⚠ Counter exhausted (reached zero)")
                break

        final_value = ts.mcounter_get(COUNTER_INDEX)

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print(f"\n=== SUMMARY ===")
        print(f"Counter {COUNTER_INDEX} statistics:")
        if counter_exists:
            print(f"  Starting value (this run): {current_value}")
        else:
            print(f"  Starting value (this run): {INITIAL_VALUE}")
        print(f"  Final value:               {final_value}")
        print(f"  Successful updates:        {updates_successful + 1}")

        print("\n=== COUNTER BEHAVIOR ===")
        print("TROPIC01 monotonic counters DECREMENT (count down):")
        print("  • Start with initial value (e.g., 100)")
        print("  • Each update decrements by 1")
        print("  • When reaching 0, counter is exhausted")
        print("  • Cannot increment - only decrement")
        print("  • Can be reinitialized with mcounter_init()")
        print("\nThis provides:")
        print("  • Limited-use tokens (N operations allowed)")
        print("  • Countdown timers")
        print("  • Usage quotas")

        print("\n=== USE CASES ===")
        print("Monotonic counters are ideal for:")
        print("  • Rate limiting (N operations remaining)")
        print("  • Limited-use credentials")
        print("  • Anti-rollback protection")
        print("  • Replay attack prevention")

        print(f"\n=== NOTE ===")
        print(f"Counter {COUNTER_INDEX} remains at value {final_value}")
        print("It will continue from this value on next run.")
        print("\nTo reset counter to a new value:")
        print(f"  ts.mcounter_init({COUNTER_INDEX}, 100)  # Reinitialize to 100")

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
