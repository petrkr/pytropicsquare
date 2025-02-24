
from .. import TropicSquare

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256


class TropicSquareCPython(TropicSquare):
    def __init__(self, spi, cs):
        self._spi = spi
        self._cs = cs
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
        ehpriv = X25519PrivateKey.generate()
        ehpubraw = ehpriv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        ehprivraw = ehpriv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

        return (ehprivraw, ehpubraw)


    def _hkdf(self, salt, shared_secret, length = 1):
        result = HKDF(algorithm=SHA256(),
                    length=length * 32,
                    salt=salt,
                    info=None).derive(shared_secret)

        if length > 1:
            return [result[i*32:(i+1)*32] for i in range(length)]
        else:
            return result


    def _x25519_exchange(self, private_bytes, public_bytes):
        priv = X25519PrivateKey.from_private_bytes(private_bytes)
        return priv.exchange(X25519PublicKey.from_public_bytes(public_bytes))


    def _aesgcm(self, key):
        return AESGCM(key)
