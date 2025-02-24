import hashlib
from random import getrandbits

from tropicsquare import TropicSquare
from tropicsquare.ports.micropython.hkdf import HKDF
from tropicsquare.ports.micropython.x25519 import X25519


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


    def _get_ephemeral_keypair(self):
        ehpriv = b''
        for _ in range(8):
            ehpriv += getrandbits(32).to_bytes(4, "big")

        return (ehpriv, X25519.pubkey(ehpriv))


    def _hkdf(self, salt, shared_secret, length = 1):
        result = HKDF.derive(salt, shared_secret, length * 32)
        if length > 1:
            return [result[i*32:(i+1)*32] for i in range(length)]
        else:
            return result


    def _x25519_exchange(self, private_bytes, public_bytes):
        return X25519.exchange(private_bytes, public_bytes)
