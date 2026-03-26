import sys
import types

import pytest

from tropicsquare.exceptions import TropicSquareError
from tropicsquare.transports.ftdi_mpsse import FtdiMpsseTransport


class FakeSpiPort:
    def __init__(self):
        self.calls = []

    def exchange(self, out=b"", readlen=0, start=True, stop=True, duplex=False, droptail=0):
        self.calls.append(("exchange", bytes(out), readlen, start, stop, duplex, droptail))
        return bytes(range(len(out)))

    def read(self, readlen=0, start=True, stop=True, droptail=0):
        self.calls.append(("read", readlen, start, stop, droptail))
        return b"\xaa" * readlen

    def force_select(self, level=None, cs_hold=0):
        self.calls.append(("force_select", level, cs_hold))


def test_native_cs_keeps_transaction_open():
    spi = FakeSpiPort()
    transport = FtdiMpsseTransport(spi)

    transport._cs_low()
    rx = transport._transfer(b"\x10\x20")
    data = transport._read(2)
    transport._cs_high()

    assert rx == b"\x00\x01"
    assert data == b"\xaa\xaa"
    assert spi.calls == [
        ("exchange", b"\x10\x20", 0, True, False, True, 0),
        ("read", 2, False, False, 0),
        ("force_select", True, 0),
    ]


def test_init_validates_spi_port():
    with pytest.raises(TropicSquareError) as exc_info:
        FtdiMpsseTransport(object())

    assert "spi must provide exchange()" in str(exc_info.value)
