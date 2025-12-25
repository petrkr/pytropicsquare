#!/usr/bin/env python3
"""
NetworkUART-SPI Server

This server bridges TCP/IP network connections to a UART-SPI interface.
It receives binary SPI commands over the network and forwards them to
a UART-based SPI bridge device (e.g., /dev/ttyACM0).

Usage:
    python networkuartspi-server.py [options]

Options:
    --port PORT        Serial port path (default: /dev/ttyACM0)
    --baudrate BAUD    Serial baudrate (default: 115200)
    --listen PORT      TCP port to listen on (default: 12345)
    --host HOST        Host address to bind to (default: 0.0.0.0)
"""

import socket
import sys
import argparse
from uartspi import UartSPI

# Command constants (same as NetworkSPI protocol)
COMMAND_READ = b'\x01'
COMMAND_READINTO = b'\x02'
COMMAND_WRITE = b'\x04'
COMMAND_WRITE_READINTO = b'\x08'
COMMAND_CS_LOW = b'\x10'
COMMAND_CS_HIGH = b'\x20'


def handle_client(conn, uart_spi, verbose=False):
    """Handle a single client connection."""
    try:
        while True:
            # Read one byte command code
            command = conn.recv(1)
            if not command:
                break  # Connection closed

            if command == COMMAND_READINTO:
                # Read length
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                if verbose:
                    print(f"READINTO: length={length}")

                # Prepare buffer and read from UART-SPI
                rx_buf = bytearray(length)
                uart_spi.readinto(rx_buf)

                # Send back the data
                conn.send(rx_buf)

                if verbose:
                    print(f"  RX: {rx_buf.hex()}")

            elif command == COMMAND_WRITE:
                # Read length
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                # Receive data bytes
                data = b''
                while len(data) < length:
                    chunk = conn.recv(length - len(data))
                    if not chunk:
                        break
                    data += chunk
                if len(data) != length:
                    break  # Incomplete data received

                if verbose:
                    print(f"WRITE: length={length}")
                    print(f"  TX: {data.hex()}")

                # Write to UART-SPI
                uart_spi.write(data)

            elif command == COMMAND_READ:
                # Read length
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                if verbose:
                    print(f"READ: length={length}")

                # Read from UART-SPI
                data = uart_spi.read(length)

                # Send back the data
                conn.send(data)

                if verbose:
                    print(f"  RX: {data.hex()}")

            elif command == COMMAND_WRITE_READINTO:
                # Read length
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                # Receive data bytes
                data = b''
                while len(data) < length:
                    chunk = conn.recv(length - len(data))
                    if not chunk:
                        break
                    data += chunk
                if len(data) != length:
                    break  # Incomplete data received

                if verbose:
                    print(f"WRITE_READINTO: length={length}")
                    print(f"  TX: {data.hex()}")

                # Prepare buffers for UART-SPI transfer
                tx_buf = bytearray(data)
                rx_buf = bytearray(length)
                uart_spi.write_readinto(tx_buf, rx_buf)

                # Send back the response
                conn.send(rx_buf)

                if verbose:
                    print(f"  RX: {rx_buf.hex()}")

            elif command == COMMAND_CS_LOW:
                if verbose:
                    print("CS_LOW")
                uart_spi.set_cs(0)
                conn.send(b'\x00')  # ACK

            elif command == COMMAND_CS_HIGH:
                if verbose:
                    print("CS_HIGH")
                uart_spi.set_cs(1)
                conn.send(b'\x00')  # ACK

            else:
                # Unknown command
                print(f"Unknown command: {command.hex()}")
                break

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='NetworkUART-SPI Server - Bridge TCP/IP to UART-SPI'
    )
    parser.add_argument(
        '--port',
        default='/dev/ttyACM0',
        help='Serial port path (default: /dev/ttyACM0)'
    )
    parser.add_argument(
        '--baudrate',
        type=int,
        default=115200,
        help='Serial baudrate (default: 115200)'
    )
    parser.add_argument(
        '--listen',
        type=int,
        default=12345,
        help='TCP port to listen on (default: 12345)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host address to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Initialize UART-SPI interface
    print(f"Initializing UART-SPI on {args.port} at {args.baudrate} baud...")
    try:
        uart_spi = UartSPI(args.port, args.baudrate)
    except Exception as e:
        print(f"Failed to initialize UART-SPI: {e}")
        sys.exit(1)

    # Set up TCP server
    addr = socket.getaddrinfo(args.host, args.listen)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print(f"NetworkUART-SPI server listening on {args.host}:{args.listen}")
    print("Waiting for connections...")

    try:
        while True:
            conn, client_addr = s.accept()
            print(f"Client connected from {client_addr}")
            handle_client(conn, uart_spi, verbose=args.verbose)
            print(f"Client disconnected: {client_addr}")
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        s.close()
        uart_spi.close()


if __name__ == '__main__':
    main()
