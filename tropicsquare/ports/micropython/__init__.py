from random import getrandbits

from tropicsquare import TropicSquare
from tropicsquare.ports.micropython.hkdf import HKDF
from tropicsquare.ports.micropython.x25519 import X25519
from tropicsquare.ports.micropython.aesgcm import AESGCM


class TropicSquareMicroPython(TropicSquare):
    def __init__(self, spi, cs, gpo=None):
        self._gpo = gpo
        super().__init__(spi, cs)

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


    def _aesgcm(self, key):
        return AESGCM(key)
