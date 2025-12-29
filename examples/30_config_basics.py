#!/usr/bin/env python3
"""Example 30: Configuration Basics - Reading R-CONFIG and I-CONFIG

This example demonstrates how to read and understand the TROPIC01's
configuration registers using the R-CONFIG and I-CONFIG spaces.

It shows:
- Reading R-CONFIG (Reversible configuration)
- Reading I-CONFIG (Irreversible configuration)
- Computing effective configuration (R & I)
- Understanding configuration hierarchy

Configuration Spaces:
- R-CONFIG: Reversible - can be modified and changed back
- I-CONFIG: Irreversible - once written, cannot be reversed
- Effective: R & I (bitwise AND) - the actual active configuration

This example reads the CFG_UAP_PING register which controls permissions
for the ping command. This is a safe, read-only demonstration.

NOTE: This example only demonstrates READ operations. Write operations
      are not implemented in the current library version.

This example works on both CPython and MicroPython platforms.

Usage:
    # With Network SPI bridge (default)
    python 30_config_basics.py [host] [port]
    micropython 30_config_basics.py  # ESP32 will use defaults

    # With direct SPI (uncomment SPI transport section)
    micropython 30_config_basics.py

    # With UART bridge (uncomment UART transport section, Unix/CPython only)
    python 30_config_basics.py [port]
"""

from tropicsquare import TropicSquare
from tropicsquare.constants.pairing_keys import *
from tropicsquare.constants.config import CFG_UAP_PING
from tropicsquare.exceptions import (
    TropicSquareError,
    TropicSquareAlarmError,
    TropicSquareHandshakeError,
    TropicSquareTimeoutError,
    TropicSquareCRCError,
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

def main():
    """Read and display configuration registers.

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
        # READ R-CONFIG (Reversible)
        # ======================================================================
        print("\n=== READING R-CONFIG (Reversible) ===")
        print("Register: CFG_UAP_PING (User Access Policy for Ping command)")

        r_config = ts.r_config_read(CFG_UAP_PING)

        print(f"\nR-CONFIG:")
        print(f"  Raw bytes: {r_config.to_bytes().hex()}")
        print(f"  Parsed:    {r_config}")
        print(f"\nR-CONFIG is Reversible - can be modified and changed back")

        # ======================================================================
        # READ I-CONFIG (Irreversible)
        # ======================================================================
        print("\n=== READING I-CONFIG (Irreversible) ===")

        i_config = ts.i_config_read(CFG_UAP_PING)

        print(f"\nI-CONFIG:")
        print(f"  Raw bytes: {i_config.to_bytes().hex()}")
        print(f"  Parsed:    {i_config}")
        print(f"\nI-CONFIG is Irreversible - once written, cannot be reversed")

        # ======================================================================
        # COMPUTE EFFECTIVE CONFIGURATION
        # ======================================================================
        print("\n=== EFFECTIVE CONFIGURATION (R & I) ===")

        # Effective = R-CONFIG & I-CONFIG (bitwise AND)
        ConfigClass = type(r_config)
        effective = ConfigClass(r_config._value & i_config._value)

        print(f"\nEffective (R & I):")
        print(f"  Raw bytes: {effective.to_bytes().hex()}")
        print(f"  Parsed:    {effective}")

        print(f"\nThe effective configuration is the bitwise AND of R and I")
        print(f"This represents the actual active configuration in the chip")

        # ======================================================================
        # DETAILED FIELD COMPARISON
        # ======================================================================
        print("\n=== DETAILED FIELD COMPARISON ===")
        print(f"{'Field':<25} {'R-CONFIG':<10} {'I-CONFIG':<10} {'Effective':<10}")
        print("-" * 60)

        r_dict = r_config.to_dict()
        i_dict = i_config.to_dict()
        eff_dict = effective.to_dict()

        for field_name in r_dict.keys():
            r_value = r_dict[field_name]
            i_value = i_dict[field_name]
            eff_value = eff_dict[field_name]

            # Handle nested dictionaries (UAP permission fields)
            if isinstance(r_value, dict):
                print(f"\n{field_name}:")
                for slot_name in r_value.keys():
                    r_slot = str(r_value[slot_name])
                    i_slot = str(i_value[slot_name])
                    eff_slot = str(eff_value[slot_name])
                    print(f"  {slot_name:<23} {r_slot:<10} {i_slot:<10} {eff_slot:<10}")
            else:
                r_str = str(r_value)
                i_str = str(i_value)
                eff_str = str(eff_value)
                print(f"{field_name:<25} {r_str:<10} {i_str:<10} {eff_str:<10}")

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print("\n=== CONFIGURATION HIERARCHY ===")
        print("R-CONFIG (Reversible):")
        print("  • Can be modified and changed back")
        print("  • Used for temporary or adjustable settings")
        print("  • Typically set by device manufacturer or firmware")
        print("\nI-CONFIG (Irreversible):")
        print("  • Once written, cannot be changed back")
        print("  • Used for permanent restrictions")
        print("  • Typically set once during provisioning")
        print("\nEffective Configuration (R & I):")
        print("  • Bitwise AND of R-CONFIG and I-CONFIG")
        print("  • Represents actual active permissions")
        print("  • Most restrictive value wins")

        print("\n=== NOTE ===")
        print("This example demonstrates READ operations only.")
        print("Configuration WRITE is not implemented in current library version.")

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
