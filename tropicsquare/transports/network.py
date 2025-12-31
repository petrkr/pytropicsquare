"""Network SPI Transport Implementation

This module provides a network-based SPI transport implementation.
for https://github.com/petrkr/netbridge32 SPI bridge
"""

from tropicsquare.transports import L1Transport
from tropicsquare.exceptions import TropicSquareError

import socket

class NetworkSpiTransport(L1Transport):
    """L1 transport for network-based SPI bridge.

        :param host: Hostname or IP address of the SPI bridge
        :param port: Port number for the SPI connection (default: 12345)
        :param timeout: Socket timeout in seconds (default: 5.0)
    """

    COMMAND_READ = b'\x01'
    COMMAND_WRITE_READINTO = b'\x08'

    COMMAND_CS_LOW = b'\x10'
    COMMAND_CS_HIGH = b'\x20'

    def __init__(self, host: str, port: int = 12345, timeout: float = 5.0):
        """Initialize Network SPI transport.

        :param host: Hostname or IP address of the SPI bridge
        :param port: Port number for the SPI connection (default: 12345)
        :param timeout: Socket timeout in seconds (default: 5.0)
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

        hostport = socket.getaddrinfo(host, port)
        self._sock = socket.socket()
        self._sock.connect(hostport[0][-1])


    def _transfer(self, write_buf: bytes) -> bytes:
        command = self.COMMAND_WRITE_READINTO
        data = bytes(write_buf)
        length = len(data)
        packet = command + length.to_bytes(4, 'big') + data
        self._sock.send(packet)

        received = b''
        while len(received) < length:
            chunk = self._sock.recv(length - len(received))
            if not chunk:
                raise RuntimeError("Connection lost during SPI transfer")
            received += chunk

        return received


    def _read(self, length: int) -> bytes:
        command = self.COMMAND_READ
        packet = command + length.to_bytes(4, 'big')
        self._sock.send(packet)

        received = b''
        while len(received) < length:
            chunk = self._sock.recv(length - len(received))
            if not chunk:
                raise Exception("Connection lost during SPI transfer")
            received += chunk

        return received


    def _set_cs(self, state: bool):
        """Sends a command (0x01) to set the chip select state.
           The state is sent as 1 byte (0 for low, 1 for high)."""
        command = self.COMMAND_CS_HIGH if state else self.COMMAND_CS_LOW
        self._sock.send(command)

        ack = self._sock.recv(1)
        if ack != b'\x00':
            raise RuntimeError("Chip select command failed, ack: " + str(ack))


    def _cs_low(self) -> None:
        self._set_cs(False)


    def _cs_high(self) -> None:
        self._set_cs(True)
