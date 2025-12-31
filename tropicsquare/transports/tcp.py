"""TCP Transport for libtropic Model/Simulator

This module provides a TCP transport implementation that communicates
with the TROPIC01 model/simulator server using the libtropic tagged protocol.

The transport enables pytropicsquare to work with the same model/simulator
infrastructure that libtropic uses, making it useful for:

- Hardware-in-the-loop testing
- Chip simulation and development
- Cross-platform testing (CPython and MicroPython)

Protocol Details:
    The transport implements the libtropic TCP protocol with tagged messages:

    - Buffer format:

        - tag (1)
        - length (2 LE)
        - payload (0-256)

    - Request-response pattern with tag validation
    - Automatic retry logic for network operations

Example::

    from tropicsquare import TropicSquare
    from tropicsquare.transports.tcp import TcpTransport

    # Connect to model server
    transport = TcpTransport("127.0.0.1")
    ts = TropicSquare(transport)

    # Use chip normally
    print(ts.chipid)

:note: Server must be running libtropic-compatible model/simulator from https://github.com/tropicsquare/ts-tvl/
"""

import socket
from tropicsquare.transports import L1Transport
from tropicsquare.exceptions import TropicSquareError, TropicSquareTimeoutError


class TcpTransport(L1Transport):
    """L1 transport for TCP connection to libtropic model/simulator.

    Implements the libtropic tagged protocol for communicating with
    the TROPIC01 model/simulator server via TCP socket.

    The transport maps L1 SPI operations to tagged TCP commands:

    - ``_cs_low()`` → TAG_CSN_LOW (0x01)
    - ``_cs_high()`` → TAG_CSN_HIGH (0x02)
    - ``_transfer()`` → TAG_SPI_SEND (0x03)
    - ``_read()`` → TAG_SPI_SEND (0x03) with dummy bytes

    :param host: Hostname or IP address of the model server
    :param port: Port number for the TCP connection (default: 28992)
    :param timeout: Socket timeout in seconds (default: 5.0)

    :raises TropicSquareError: If connection fails

    Example::

        transport = TcpTransport("127.0.0.1")
        ts = TropicSquare(transport)
        print(ts.chipid)
    """

    # Protocol tags
    TAG_CSN_LOW = 0x01
    TAG_CSN_HIGH = 0x02
    TAG_SPI_SEND = 0x03
    TAG_WAIT = 0x06
    TAG_INVALID = 0xfd
    TAG_UNSUPPORTED = 0xfe

    # Protocol limits
    MAX_PAYLOAD_LEN = 256
    MAX_BUFFER_LEN = 259  # 3 (tag + length) + 256 (payload)
    TX_ATTEMPTS = 3
    RX_ATTEMPTS = 3

    def __init__(self, host: str, port: int = 28992, timeout: float = 5.0):
        """Initialize TCP transport.

        :param host: Hostname or IP address of the model server
        :param port: Port number for the TCP connection (default: 28992)
        :param timeout: Socket timeout in seconds (default: 5.0)

        :raises TropicSquareError: If connection fails
        """
        try:
            hostport = socket.getaddrinfo(host, port)
            self._sock = socket.socket()
            self._sock.settimeout(timeout)
            self._sock.connect(hostport[0][-1])
        except Exception as e:
            self._sock.close()
            raise TropicSquareError(
                f"Failed to connect to {host}:{port}: {e}"
            )


    def _transfer(self, tx_data: bytes) -> bytes:
        """SPI bidirectional transfer.

        Corresponds to SPI write_readinto operation.
        Sends tx_data and receives same number of bytes back.

        :param tx_data: Data to transmit

        :returns: Received data (same length as tx_data)

        :raises TropicSquareError: If transfer length mismatch occurs
        """
        rx_data = self._communicate(self.TAG_SPI_SEND, tx_data)

        if len(rx_data) != len(tx_data):
            raise TropicSquareError(
                f"Transfer length mismatch: sent {len(tx_data)}, "
                f"received {len(rx_data)}"
            )

        return rx_data


    def _read(self, length: int) -> bytes:
        """SPI read operation.

        Corresponds to SPI read operation.
        Sends dummy bytes (all zeros) and reads response.

        :param length: Number of bytes to read

        :returns: Read data
        """
        # Send dummy bytes (all zeros) to clock out data
        return self._communicate(self.TAG_SPI_SEND, bytes(length))


    def _cs_low(self) -> None:
        """Activate chip select (CS to logic 0).

        Sends TAG_CSN_LOW command to the model server.
        """
        self._communicate(self.TAG_CSN_LOW)


    def _cs_high(self) -> None:
        """Deactivate chip select (CS to logic 1).

        Sends TAG_CSN_HIGH command to the model server.
        """
        self._communicate(self.TAG_CSN_HIGH)


    def _send_all(self, data: bytes) -> None:
        """Send all data with retry logic.

        :param data: Data to send

        :raises TropicSquareError: If send fails
        :raises TropicSquareTimeoutError: If send times out after retries
        """
        total_sent = 0
        attempts = 0

        while total_sent < len(data) and attempts < self.TX_ATTEMPTS:
            try:
                sent = self._sock.send(data[total_sent:])
                if sent == 0:
                    raise TropicSquareError("Connection lost during send")
                total_sent += sent
            except socket.timeout:
                attempts += 1
                if attempts >= self.TX_ATTEMPTS:
                    raise TropicSquareTimeoutError(
                        f"Send timeout after {attempts} attempts"
                    )
            except Exception as e:
                raise TropicSquareError(f"Send failed: {e}")

        if total_sent < len(data):
            raise TropicSquareError(
                f"Sent {total_sent}/{len(data)} bytes after {attempts} attempts"
            )


    def _recv_exact(self, num_bytes: int) -> bytes:
        """Receive exactly num_bytes with retry logic.

        :param num_bytes: Number of bytes to receive

        :returns: Received data

        :raises TropicSquareError: If receive fails or connection lost
        :raises TropicSquareTimeoutError: If receive times out after retries
        """
        received = bytearray()
        attempts = 0

        while len(received) < num_bytes and attempts < self.RX_ATTEMPTS:
            try:
                chunk = self._sock.recv(num_bytes - len(received))
                if not chunk:
                    raise TropicSquareError("Connection lost during receive")
                received.extend(chunk)
            except socket.timeout:
                attempts += 1
                if attempts >= self.RX_ATTEMPTS:
                    raise TropicSquareTimeoutError(
                        f"Receive timeout after {attempts} attempts"
                    )
            except Exception as e:
                raise TropicSquareError(f"Receive failed: {e}")

        if len(received) < num_bytes:
            raise TropicSquareError(
                f"Received {len(received)}/{num_bytes} bytes"
            )

        return bytes(received)


    def _communicate(self, tag: int, tx_payload: bytes = None) -> bytes:
        """Send tagged request and receive response.

        Implements the libtropic TCP protocol:

        1. Build TX buffer: [tag (1)][length (2 LE)][payload (0-256)]
        2. Send all bytes with retry logic
        3. Receive response header (tag + length)
        4. Validate tag matches or is error tag
        5. Receive payload if length > 0
        6. Return payload data

        :param tag: Protocol tag (TAG_CSN_LOW, TAG_CSN_HIGH, TAG_SPI_SEND, etc.)
        :param tx_payload: Optional payload data (max 256 bytes)

        :returns: Response payload (or empty bytes if no payload)

        :raises TropicSquareError: On protocol or network errors
        :raises TropicSquareTimeoutError: On timeout
        """
        # Build TX buffer: [tag][length LE][payload]
        payload_len = len(tx_payload) if tx_payload else 0

        if payload_len > self.MAX_PAYLOAD_LEN:
            raise TropicSquareError(
                f"Payload too large: {payload_len} > {self.MAX_PAYLOAD_LEN}"
            )

        tx_buffer = bytearray(self.MAX_BUFFER_LEN)
        tx_buffer[0] = tag
        tx_buffer[1] = payload_len & 0xFF  # Little-endian low byte
        tx_buffer[2] = (payload_len >> 8) & 0xFF  # Little-endian high byte

        if tx_payload:
            tx_buffer[3:3 + payload_len] = tx_payload

        tx_size = 3 + payload_len

        # Send request
        self._send_all(bytes(tx_buffer[:tx_size]))

        # Receive response header (tag + length)
        rx_header = self._recv_exact(3)
        rx_tag = rx_header[0]
        rx_len = rx_header[1] | (rx_header[2] << 8)  # Little-endian

        # Validate tag
        if rx_tag == self.TAG_INVALID:
            raise TropicSquareError(
                f"Server doesn't recognize tag {tag:#04x}"
            )
        elif rx_tag == self.TAG_UNSUPPORTED:
            raise TropicSquareError(
                f"Server doesn't support tag {tag:#04x}"
            )
        elif rx_tag != tag:
            raise TropicSquareError(
                f"Tag mismatch: sent {tag:#04x}, received {rx_tag:#04x}"
            )

        # Validate payload length
        if rx_len > self.MAX_PAYLOAD_LEN:
            raise TropicSquareError(
                f"Invalid payload length: {rx_len} > {self.MAX_PAYLOAD_LEN}"
            )

        # Receive payload if present
        if rx_len > 0:
            rx_payload = self._recv_exact(rx_len)
        else:
            rx_payload = b''

        return rx_payload
