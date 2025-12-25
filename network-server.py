#!/usr/bin/env python3
"""
Network SPI Server

This server bridges TCP/IP network connections to an L1 transport.
It receives binary SPI commands over the network and forwards them to
UART, spidev, or NetworkSPI transport.

Usage:
    python networkuartspi-server.py [options]

Options:
    --transport {uart,spidev,network}  Transport backend (default: uart)
    --port PORT                    UART port path (default: /dev/ttyACM0)
    --baudrate BAUD                UART baudrate (default: 115200)
    --spidev-bus BUS               spidev bus (default: 0)
    --spidev-device DEV            spidev device (default: 1)
    --spidev-cs-pin PIN             spidev CS GPIO pin (default: 25)
    --spidev-max-speed HZ          spidev max speed (default: 1000000)
    --spidev-gpio-chip PATH        spidev GPIO chip (default: /dev/gpiochip0)
    --net-host HOST                NetworkSPI host (default: 127.0.0.1)
    --net-port PORT                NetworkSPI port (default: 12345)
    --net-timeout SEC              NetworkSPI timeout (default: 5.0)
    --listen PORT                  TCP port to listen on (default: 12345)
    --host HOST                    Host address to bind to (default: 0.0.0.0)
"""

import argparse
import socket
import sys

from tropicsquare.transports import L1Transport

# Command constants (same as NetworkSPI protocol)
COMMAND_READ = b'\x01'
COMMAND_READINTO = b'\x02'
COMMAND_WRITE = b'\x04'
COMMAND_WRITE_READINTO = b'\x08'
COMMAND_CS_LOW = b'\x10'
COMMAND_CS_HIGH = b'\x20'


def _recv_exact(conn, length: int) -> bytes:
    data = b''
    while len(data) < length:
        chunk = conn.recv(length - len(data))
        if not chunk:
            return b''
        data += chunk
    return data


def _close_transport(transport: L1Transport) -> None:
    close_fn = getattr(transport, "close", None)
    if callable(close_fn):
        close_fn()
        return
    close_fn = getattr(transport, "_close", None)
    if callable(close_fn):
        close_fn()


def handle_client(conn, transport: L1Transport, verbose: bool = False):
    """Handle a single client connection."""
    try:
        while True:
            # Read one byte command code
            command = _recv_exact(conn, 1)
            if not command:
                break  # Connection closed

            if command == COMMAND_READINTO:
                # Read length
                len_bytes = _recv_exact(conn, 4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                if verbose:
                    print(f"READINTO: length={length}")

                # Read from transport
                data = transport._read(length)
                conn.send(data)

                if verbose:
                    print(f"  RX: {data.hex()}")

            elif command == COMMAND_WRITE:
                # Read length
                len_bytes = _recv_exact(conn, 4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                # Receive data bytes
                data = _recv_exact(conn, length)
                if len(data) != length:
                    break  # Incomplete data received

                if verbose:
                    print(f"WRITE: length={length}")
                    print(f"  TX: {data.hex()}")

                # SPI write: transfer and ignore RX
                transport._transfer(data)

            elif command == COMMAND_READ:
                # Read length
                len_bytes = _recv_exact(conn, 4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                if verbose:
                    print(f"READ: length={length}")

                # Read from transport
                data = transport._read(length)

                # Send back the data
                conn.send(data)

                if verbose:
                    print(f"  RX: {data.hex()}")

            elif command == COMMAND_WRITE_READINTO:
                # Read length
                len_bytes = _recv_exact(conn, 4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')

                # Receive data bytes
                data = _recv_exact(conn, length)
                if len(data) != length:
                    break  # Incomplete data received

                if verbose:
                    print(f"WRITE_READINTO: length={length}")
                    print(f"  TX: {data.hex()}")

                # Transfer
                rx = transport._transfer(data)
                conn.send(rx)

                if verbose:
                    print(f"  RX: {rx.hex()}")

            elif command == COMMAND_CS_LOW:
                if verbose:
                    print("CS_LOW")
                transport._cs_low()
                conn.send(b'\x00')  # ACK

            elif command == COMMAND_CS_HIGH:
                if verbose:
                    print("CS_HIGH")
                transport._cs_high()
                conn.send(b'\x00')  # ACK

            else:
                # Unknown command
                print(f"Unknown command: {command.hex()}")
                break

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()


def _create_transport(args) -> L1Transport:
    if args.transport == "uart":
        from tropicsquare.transports.uart import UartTransport
        print(f"Initializing UART transport on {args.port} at {args.baudrate} baud...")
        return UartTransport(args.port, args.baudrate)

    if args.transport == "spidev":
        from tropicsquare.transports.spidev import SpiDevTransport
        print(
            "Initializing spidev transport on "
            f"bus={args.spidev_bus}, device={args.spidev_device}, "
            f"cs_pin={args.spidev_cs_pin}, max_speed={args.spidev_max_speed}..."
        )
        return SpiDevTransport(
            bus=args.spidev_bus,
            device=args.spidev_device,
            cs_pin=args.spidev_cs_pin,
            max_speed_hz=args.spidev_max_speed,
            gpio_chip=args.spidev_gpio_chip,
        )

    if args.transport == "network":
        from tropicsquare.transports.network import NetworkSpiTransport
        print(
            "Initializing Network SPI transport on "
            f"{args.net_host}:{args.net_port}..."
        )
        return NetworkSpiTransport(
            host=args.net_host,
            port=args.net_port,
            timeout=args.net_timeout,
        )

    raise RuntimeError(f"Unsupported transport: {args.transport}")


def main():
    parser = argparse.ArgumentParser(
        description='Network SPI Server - Bridge TCP/IP to L1 transport'
    )
    parser.add_argument(
        '--transport',
        choices=['uart', 'spidev', 'network'],
        default='uart',
        help='Transport backend (default: uart)'
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
        '--spidev-bus',
        type=int,
        default=0,
        help='spidev bus (default: 0)'
    )
    parser.add_argument(
        '--spidev-device',
        type=int,
        default=1,
        help='spidev device (default: 1)'
    )
    parser.add_argument(
        '--spidev-cs-pin',
        type=int,
        default=25,
        help='spidev CS GPIO pin (default: 25)'
    )
    parser.add_argument(
        '--spidev-max-speed',
        type=int,
        default=1000000,
        help='spidev max speed (default: 1000000)'
    )
    parser.add_argument(
        '--spidev-gpio-chip',
        default='/dev/gpiochip0',
        help='spidev GPIO chip (default: /dev/gpiochip0)'
    )
    parser.add_argument(
        '--net-host',
        default='127.0.0.1',
        help='NetworkSPI host (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--net-port',
        type=int,
        default=12345,
        help='NetworkSPI port (default: 12345)'
    )
    parser.add_argument(
        '--net-timeout',
        type=float,
        default=5.0,
        help='NetworkSPI timeout (default: 5.0)'
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

    try:
        transport = _create_transport(args)
    except Exception as e:
        print(f"Failed to initialize transport: {e}")
        sys.exit(1)

    # Set up TCP server
    addr = socket.getaddrinfo(args.host, args.listen)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print(f"Network SPI server listening on {args.host}:{args.listen}")
    print("Waiting for connections...")

    try:
        while True:
            conn, client_addr = s.accept()
            print(f"Client connected from {client_addr}")
            handle_client(conn, transport, verbose=args.verbose)
            print(f"Client disconnected: {client_addr}")
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        s.close()
        _close_transport(transport)


if __name__ == '__main__':
    main()
