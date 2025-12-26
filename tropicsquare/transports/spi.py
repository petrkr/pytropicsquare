"""SPI Transport Implementation

This module provides SPI transport implementation for MicroPython machine.SPI interface.
"""

from tropicsquare.transports import L1Transport


class SpiTransport(L1Transport):
    """L1 transport for MicroPython machine.SPI.

    :param spi: SPI interface object (e.g., machine.SPI instance)
    :param cs: Chip select pin object (e.g., machine.Pin instance)
    """


    def __init__(self, spi, cs):
        """Initialize SPI transport.

        :param spi: SPI interface object
        :param cs: Chip select pin object
        """
        self._spi = spi
        self._cs = cs
        # Initialize CS to default state (high = inactive)
        self._cs.value(1)


    def _transfer(self, tx_data: bytes) -> bytes:
        """SPI transfer using write_readinto.

        :param tx_data: Data to transmit
        :type tx_data: bytes
        :returns: Received data
        :rtype: bytes
        """
        rx_buffer = bytearray(len(tx_data))
        tx_buffer = bytearray(tx_data)
        self._spi.write_readinto(tx_buffer, rx_buffer)
        return bytes(rx_buffer)


    def _read(self, length: int) -> bytes:
        """SPI read operation.

        :param length: Number of bytes to read
        :type length: int
        :returns: Read data
        :rtype: bytes
        """
        return self._spi.read(length)


    def _cs_low(self) -> None:
        """Activate chip select (set to 0)."""
        self._cs.value(0)


    def _cs_high(self) -> None:
        """Deactivate chip select (set to 1)."""
        self._cs.value(1)
