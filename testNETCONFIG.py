#!/usr/bin/env python3
"""
NetworkUART-SPI Config Test Script (Universal version)

This script automatically detects the platform (CPython or MicroPython)
and uses the appropriate TropicSquare implementation.

Usage:
    python3 testNETCONFIG-universal.py [host] [port]
    micropython testNETCONFIG-universal.py [host] [port]

Arguments:
    host    Server hostname or IP address (default: 10.200.0.176)
    port    Server TCP port (default: 12345)

Example:
    python3 testNETCONFIG-universal.py 10.200.0.176 12345
    micropython testNETCONFIG-universal.py 10.200.0.176 12345
"""

import sys

# Automatic platform detection - just import TropicSquare!
from tropicsquare import TropicSquare
from tropicsquare.exceptions import *
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)
from tropicsquare.constants.config import (
    CFG_START_UP, CFG_SENSORS, CFG_DEBUG, CFG_GPO, CFG_SLEEP_MODE,
    CFG_UAP_PAIRING_KEY_WRITE, CFG_UAP_PAIRING_KEY_READ, CFG_UAP_PAIRING_KEY_INVALIDATE,
    CFG_UAP_R_CONFIG_WRITE_ERASE, CFG_UAP_R_CONFIG_READ,
    CFG_UAP_I_CONFIG_WRITE, CFG_UAP_I_CONFIG_READ,
    CFG_UAP_PING, CFG_UAP_R_MEM_DATA_WRITE, CFG_UAP_R_MEM_DATA_READ, CFG_UAP_R_MEM_DATA_ERASE,
    CFG_UAP_RANDOM_VALUE_GET, CFG_UAP_ECC_KEY_GENERATE, CFG_UAP_ECC_KEY_STORE,
    CFG_UAP_ECC_KEY_READ, CFG_UAP_ECC_KEY_ERASE, CFG_UAP_ECDSA_SIGN, CFG_UAP_EDDSA_SIGN,
    CFG_UAP_MCOUNTER_INIT, CFG_UAP_MCOUNTER_GET, CFG_UAP_MCOUNTER_UPDATE,
    CFG_UAP_MAC_AND_DESTROY
)
from tropicsquare.config import (
    parse_config, StartUpConfig, SensorsConfig, DebugConfig, GpoConfig, SleepModeConfig
)
from tropicsquare.config.uap_pairing_key import (
    PairingKeyWriteConfig, PairingKeyReadConfig, PairingKeyInvalidateConfig
)
from tropicsquare.config.uap_rconfig_iconfig import (
    RConfigWriteEraseConfig, RConfigReadConfig, IConfigWriteConfig, IConfigReadConfig
)

from tropicsquare.transports.network import NetworkSpiTransport

def print_separator(title=""):
    """Print a separator line with optional title."""
    if title:
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)
    else:
        print("-" * 60)


def test_config_register(ts, reg_addr, reg_name):
    """Test reading and parsing a config register from both R and I spaces."""
    print_separator("Testing {} (0x{:02x})".format(reg_name, reg_addr))

    # Read R-CONFIG
    print("\nReading R-CONFIG...")
    r_data = ts.r_config_read(reg_addr)
    print("  Raw bytes: {}".format(r_data.hex()))
    r_config = parse_config(reg_addr, r_data)
    print("  Parsed: {}".format(r_config))

    # Read I-CONFIG
    print("\nReading I-CONFIG...")
    i_data = ts.i_config_read(reg_addr)
    print("  Raw bytes: {}".format(i_data.hex()))
    i_config = parse_config(reg_addr, i_data)
    print("  Parsed: {}".format(i_config))

    # Compute effective configuration (works for all config types)
    ConfigClass = type(r_config)
    effective = ConfigClass(r_config._value & i_config._value)

    if effective:
        print("\nEffective Configuration (R & I):")
        print("  {}".format(effective))

    # Print detailed fields
    print("\nDetailed fields:")
    fields_dict = r_config.to_dict()
    for field_name, r_value in fields_dict.items():
        i_value = i_config.to_dict()[field_name]
        eff_value = effective.to_dict()[field_name]

        # Handle nested dictionaries (UAP permission fields)
        if isinstance(r_value, dict):
            print("  {}:".format(field_name))
            for slot_name, r_slot_value in r_value.items():
                i_slot_value = i_value[slot_name]
                eff_slot_value = eff_value[slot_name]
                print("    {:23s} R={:5s}  I={:5s}  Eff={:5s}".format(
                    slot_name + ":",
                    str(r_slot_value),
                    str(i_slot_value),
                    str(eff_slot_value)
                ))
        else:
            print("  {:25s} R={:5s}  I={:5s}  Eff={:5s}".format(
                field_name + ":",
                str(r_value),
                str(i_value),
                str(eff_value)
            ))


def main():
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else '10.200.0.176'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 12345

    # Detect and show platform
    platform = sys.implementation.name
    print("NetworkUART-SPI Config Test (Universal)")
    print("Platform: {}".format(platform))
    print_separator()
    print("Connecting to NetworkUART-SPI server at {}:{}...".format(host, port))

    # L1 layer - Network UART-SPI
    # Automatic platform detection happens here!
    ts = TropicSquare(NetworkSpiTransport(host, port))
    print("Using: {}".format(type(ts).__name__))

    try:
        # Get chip information
        print_separator("CHIP IDENTIFICATION")
        print(ts.chipid)

        # Start secure session
        print("\nStarting secure session...")
        ts.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        print("Secure session established!")

        # Test ping
        resp = ts.ping(b"UniversalTest")
        print("Ping response: {}".format(resp))

        # Test each configuration register
        test_config_register(ts, CFG_START_UP, "CFG_START_UP")
        test_config_register(ts, CFG_SENSORS, "CFG_SENSORS")
        test_config_register(ts, CFG_DEBUG, "CFG_DEBUG")
        test_config_register(ts, CFG_GPO, "CFG_GPO")
        test_config_register(ts, CFG_SLEEP_MODE, "CFG_SLEEP_MODE")

        # Test UAP (User Access Policy) configuration registers
        test_config_register(ts, CFG_UAP_PAIRING_KEY_WRITE, "CFG_UAP_PAIRING_KEY_WRITE")
        test_config_register(ts, CFG_UAP_PAIRING_KEY_READ, "CFG_UAP_PAIRING_KEY_READ")
        test_config_register(ts, CFG_UAP_PAIRING_KEY_INVALIDATE, "CFG_UAP_PAIRING_KEY_INVALIDATE")
        test_config_register(ts, CFG_UAP_R_CONFIG_WRITE_ERASE, "CFG_UAP_R_CONFIG_WRITE_ERASE")
        test_config_register(ts, CFG_UAP_R_CONFIG_READ, "CFG_UAP_R_CONFIG_READ")
        test_config_register(ts, CFG_UAP_I_CONFIG_WRITE, "CFG_UAP_I_CONFIG_WRITE")
        test_config_register(ts, CFG_UAP_I_CONFIG_READ, "CFG_UAP_I_CONFIG_READ")
        test_config_register(ts, CFG_UAP_PING, "CFG_UAP_PING")
        test_config_register(ts, CFG_UAP_R_MEM_DATA_WRITE, "CFG_UAP_R_MEM_DATA_WRITE")
        test_config_register(ts, CFG_UAP_R_MEM_DATA_READ, "CFG_UAP_R_MEM_DATA_READ")
        test_config_register(ts, CFG_UAP_R_MEM_DATA_ERASE, "CFG_UAP_R_MEM_DATA_ERASE")
        test_config_register(ts, CFG_UAP_RANDOM_VALUE_GET, "CFG_UAP_RANDOM_VALUE_GET")
        test_config_register(ts, CFG_UAP_ECC_KEY_GENERATE, "CFG_UAP_ECC_KEY_GENERATE")
        test_config_register(ts, CFG_UAP_ECC_KEY_STORE, "CFG_UAP_ECC_KEY_STORE")
        test_config_register(ts, CFG_UAP_ECC_KEY_READ, "CFG_UAP_ECC_KEY_READ")
        test_config_register(ts, CFG_UAP_ECC_KEY_ERASE, "CFG_UAP_ECC_KEY_ERASE")
        test_config_register(ts, CFG_UAP_ECDSA_SIGN, "CFG_UAP_ECDSA_SIGN")
        test_config_register(ts, CFG_UAP_EDDSA_SIGN, "CFG_UAP_EDDSA_SIGN")
        test_config_register(ts, CFG_UAP_MCOUNTER_INIT, "CFG_UAP_MCOUNTER_INIT")
        test_config_register(ts, CFG_UAP_MCOUNTER_GET, "CFG_UAP_MCOUNTER_GET")
        test_config_register(ts, CFG_UAP_MCOUNTER_UPDATE, "CFG_UAP_MCOUNTER_UPDATE")
        test_config_register(ts, CFG_UAP_MAC_AND_DESTROY, "CFG_UAP_MAC_AND_DESTROY")

        # Summary
        print_separator("TEST SUMMARY")
        print("Platform: {}".format(platform))
        print("Implementation: {}".format(type(ts).__name__))
        print("All config registers read successfully!")
        print("Config subsystem is working correctly.")

        # Abort session
        print("\nAborting secure session...")
        ts.abort_secure_session()
        print("Session closed.")

        return 0

    except TropicSquareAlarmError as e:
        print("\nALARM: {}".format(e))
        return 1
    except TropicSquareHandshakeError as e:
        print("\nHANDSHAKE ERROR: {}".format(e))
        return 1
    except TropicSquareTimeoutError as e:
        print("\nTIMEOUT: {}".format(e))
        return 1
    except TropicSquareCRCError as e:
        print("\nCRC ERROR: {}".format(e))
        return 1
    except TropicSquareError as e:
        print("\nTROPICSQUARE ERROR: {}".format(e))
        return 1
    except Exception as e:
        print("\nUNEXPECTED ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
