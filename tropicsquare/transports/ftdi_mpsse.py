"""FTDI MPSSE SPI transport."""

from tropicsquare.transports import L1Transport
from tropicsquare.exceptions import TropicSquareError


class FtdiMpsseTransport(L1Transport):
    """L1 transport for FTDI MPSSE SPI bridges.

    :param spi: Configured PyFtdi ``SpiPort`` instance
    """

    def __init__(self, spi) -> None:
        self._selected = False
        self._started = False
        self._spi = spi


    def _transfer(self, tx_data: bytes) -> bytes:
        start = self._consume_start_flag()
        return self._spi.exchange(
            tx_data,
            start=start,
            stop=False,
            duplex=True,
        )


    def _read(self, length: int) -> bytes:
        if not self._selected:
            raise RuntimeError("SPI read attempted with chip select inactive")

        start = self._consume_start_flag()
        return self._spi.read(
            length,
            start=start,
            stop=False,
        )


    def _cs_low(self) -> None:
        if self._selected:
            return

        self._selected = True
        self._started = False


    def _cs_high(self) -> None:
        if not self._selected:
            return

        if self._started:
            self._spi.force_select(True)

        self._selected = False
        self._started = False


    def _consume_start_flag(self) -> bool:
        if not self._selected:
            raise RuntimeError("SPI transfer attempted with chip select inactive")

        start = not self._started
        self._started = True
        return start
