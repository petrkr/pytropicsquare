
from .. import TropicSquare


class TropicSquareMicroPython(TropicSquare):
    def __init__(self, spi, cs, gpo = None):
        self._spi = spi
        self._cs = cs
        self._gpo = gpo

        super().__init__()


    def _spi_cs(self, value):
        self._cs.value(value)


    def _spi_write(self, data):
        self._spi.write(data)


    def _spi_read(self, len: int) -> bytes:
        return self._spi.read(len)


    def _spi_readinto(self, buffer: bytearray):
        self._spi.readinto(buffer)


    def _spi_write_readinto(self, tx_buffer, rx_buffer: bytearray):
        self._spi.write_readinto(tx_buffer, rx_buffer)
