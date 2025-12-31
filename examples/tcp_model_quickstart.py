"""Example: Using TCP Transport with TROPIC01 Model

This example demonstrates connecting to the TROPIC01 model/simulator
via TCP using the libtropic protocol.

Prerequisites:
    - TROPIC01 model server running (from https://github.com/tropicsquare/ts-tvl/)
    - Default server address: 127.0.0.1:28992
    - Compatible with both CPython and MicroPython

Usage:
    python examples/tcp_model_quickstart.py [host] [port]

Example:
    python examples/tcp_model_quickstart.py
    python examples/tcp_model_quickstart.py 192.168.1.100 28992
"""

import sys
from tropicsquare import TropicSquare
from tropicsquare.transports.tcp import TcpTransport
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)


def main():
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 28992

    print(f"Connecting to TROPIC01 model at {host}:{port}...")

    # Create transport
    transport = TcpTransport(host, port)

    # Create TropicSquare instance
    ts = TropicSquare(transport)

    print("Connected successfully!")

    # Get chip information
    print("\n=== Chip Information ===")
    print(ts.chipid)

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
    test_data = b"Hello TROPIC01 Model!"
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

    print("\n=== Test Complete ===")
    print("All operations successful!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
