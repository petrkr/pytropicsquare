#!/usr/bin/env python3
"""Example: MAC and Destroy operations for atomic PIN verification.

This example demonstrates basic usage of MAC_And_Destroy command on TROPIC01.

MAC_And_Destroy is TROPIC01's flagship feature for atomic PIN verification:
- Uses Keccak-based MAC with PUF (Physically Unclonable Function)
- Operates on 128 dedicated slots (0-127) in MAC-and-Destroy partition
- Each slot can be destroyed after failed attempt (one-time-use)
- Side-channel protection via multi-threshold Keccak engines

For complete PIN verification implementation, see:
- libtropic/examples/lt_ex_macandd.c (C reference implementation)
- TROPIC01 Application Note: ODN_TR01_app_002_pin_verif.pdf

Requirements:
- TROPIC01 model server running at 127.0.0.1:28992
- Active secure session

Based on TROPIC01 User API v1.1.2, Table 37 and Datasheet Rev. A.10, Section 7.9.
"""

from tropicsquare import TropicSquare
from tropicsquare.transports.tcp import TcpTransport
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)
from tropicsquare.constants import MAC_AND_DESTROY_DATA_SIZE


def main():
    """Demonstrate MAC and Destroy basic operations."""
    print("=" * 70)
    print("TROPIC01: MAC and Destroy Example")
    print("=" * 70)
    print("\nNOTE: This demonstrates basic MAC_And_Destroy command usage.")
    print("For complete PIN verification workflow, see libtropic C examples.")
    print()

    # Connect to model server
    print("1. Connecting to TROPIC01 model server at 127.0.0.1:28992...")
    transport = TcpTransport("127.0.0.1", 28992)
    ts = TropicSquare(transport)
    print("   ✓ Connected")

    # Start secure session
    print("\n2. Starting secure session...")
    ts.start_secure_session(
        FACTORY_PAIRING_KEY_INDEX,
        FACTORY_PAIRING_PRIVATE_KEY_PROD0,
        FACTORY_PAIRING_PUBLIC_KEY_PROD0
    )
    print("   ✓ Secure session established")

    # Example 1: Basic MAC and destroy with 32-byte data
    print("\n3. Example 1: Basic MAC_And_Destroy operation")
    print(f"   DATA_IN/DATA_OUT size: exactly {MAC_AND_DESTROY_DATA_SIZE} bytes (API spec)")

    # Input data - exactly 32 bytes
    data_in = b"Hello TROPIC01 MAC & Destroy"
    data_in = data_in[:MAC_AND_DESTROY_DATA_SIZE].ljust(MAC_AND_DESTROY_DATA_SIZE, b'\x00')

    print(f"   DATA_IN:  {data_in[:24].hex()}... ({len(data_in)} bytes)")

    slot = 0
    data_out = ts.mac_and_destroy(slot, data_in)

    print(f"   Slot:     {slot}")
    print(f"   DATA_OUT: {data_out[:24].hex()}... ({len(data_out)} bytes)")
    print("   ✓ MAC_And_Destroy executed")

    # Example 2: Verify determinism (same input -> same output)
    print("\n4. Example 2: Deterministic behavior")
    print("   Testing: same DATA_IN + same slot → same DATA_OUT")

    test_data = b"Determinism test 32 bytes___"
    test_data = test_data[:MAC_AND_DESTROY_DATA_SIZE].ljust(MAC_AND_DESTROY_DATA_SIZE, b'\x00')

    slot = 5
    output1 = ts.mac_and_destroy(slot, test_data)
    output2 = ts.mac_and_destroy(slot, test_data)

    print(f"   Output 1: {output1[:16].hex()}...")
    print(f"   Output 2: {output2[:16].hex()}...")

    if output1 == output2:
        print("   ✓ Deterministic: same input → same output")
    else:
        print("   ✗ Unexpected: different outputs!")

    # Example 3: Slot independence (different slots -> different outputs)
    print("\n5. Example 3: Slot independence")
    print("   Testing: same DATA_IN + different slots → different DATA_OUT")

    same_input = b"X" * MAC_AND_DESTROY_DATA_SIZE

    out_slot10 = ts.mac_and_destroy(10, same_input)
    out_slot11 = ts.mac_and_destroy(11, same_input)

    print(f"   Slot 10:  {out_slot10[:16].hex()}...")
    print(f"   Slot 11:  {out_slot11[:16].hex()}...")

    if out_slot10 != out_slot11:
        print("   ✓ Slot-dependent: different slots → different outputs")
    else:
        print("   ✗ Unexpected: same output for different slots!")

    # Example 4: Understanding PIN verification usage
    print("\n6. Example 4: How MAC_And_Destroy is used for PIN verification")
    print("   (This is simplified - see libtropic for complete implementation)")
    print()
    print("   PIN verification workflow:")
    print("   1. User enters variable-length PIN (e.g., 4-8 bytes)")
    print("   2. Host computes: v = HMAC-SHA256(key=0, data=PIN)")
    print("   3. Host calls: data_out = mac_and_destroy(slot, v)")
    print("   4. Host uses data_out to derive encryption key")
    print("   5. Slot is destroyed (one-time-use per attempt)")
    print("   6. If PIN correct, slots are re-initialized")
    print()
    print("   Key insight: MAC_And_Destroy works with 32-byte blocks.")
    print("   Variable-length PIN is hashed by host KDF first.")

    # Example 5: Error handling
    print("\n7. Example 5: Input validation")

    # Try invalid data length
    print("   Testing invalid data length...")
    try:
        ts.mac_and_destroy(0, b"too short")
        print("   ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Caught: {e}")

    # Try invalid slot
    print("   Testing invalid slot number...")
    try:
        valid_data = b"X" * MAC_AND_DESTROY_DATA_SIZE
        ts.mac_and_destroy(128, valid_data)  # Max is 127
        print("   ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Caught: {e}")

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print()
    print("Next steps:")
    print("- See libtropic/examples/lt_ex_macandd.c for full PIN workflow")
    print("- Read ODN_TR01_app_002_pin_verif.pdf application note")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
