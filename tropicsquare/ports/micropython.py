
from .. import TropicSquare

class TropicSquareMicroPython(TropicSquare):
    def __init__(self, spi, cs, gpo = None):
        self._spi = spi
        self._cs = cs
        self._gpo = gpo

        super().__init__()
