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

    def __init__(
        self,
        host: str,
        port: int = 12345,
        timeout: float = 5.0,
        connect_timeout: float = 1.0,
    ):
        """Initialize Network SPI transport.

        :param host: Hostname or IP address of the SPI bridge
        :param port: Port number for the SPI connection (default: 12345)
        :param timeout: Socket I/O timeout in seconds (default: 5.0)
        :param connect_timeout: Connect timeout per resolved address in seconds (default: 1.0)
        """
        self._sock = None
        try:
            addrinfos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM, 0)
            errors = []
            for family, socktype, proto, _, sockaddr in addrinfos:
                sock = None
                try:
                    sock = socket.socket(family, socktype, proto)
                    sock.settimeout(connect_timeout)
                    sock.connect(sockaddr)
                    sock.settimeout(timeout)
                    self._sock = sock
                    break
                except Exception as e:
                    errors.append(f"{sockaddr}: {e}")
                    if sock is not None:
                        sock.close()
            if self._sock is None:
                if errors:
                    summary = "; ".join(errors)
                    raise OSError(summary)
                raise OSError("No resolved addresses")
        except Exception as e:
            if self._sock is not None:
                self._sock.close()
            raise TropicSquareError(
                f"Failed to connect to {host}:{port}: {e}"
            )

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
