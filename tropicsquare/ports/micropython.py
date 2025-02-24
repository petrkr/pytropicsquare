import hashlib
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


    def _hkdf(self, salt, shared_secret, length = 1):
        prk = self._hkdf_extract(salt, shared_secret)
        result = self._hkdf_expand(prk, b'', length * 32)

        if length > 1:
            return [result[i*32:(i+1)*32] for i in range(length)]
        else:
            return result


    # Internal micropython helpers
    def _hmac_sha256(self, key, message):
        blocksize = 64

        if len(key) > blocksize:
            key = hashlib.sha256(key).digest()
        # Pad key with zeros if it's shorter than blocksize
        if len(key) < blocksize:
            key = key + b'\x00' * (blocksize - len(key))
        # Create inner and outer padded keys
        o_key_pad = bytes([b ^ 0x5c for b in key])
        i_key_pad = bytes([b ^ 0x36 for b in key])
        inner_hash = hashlib.sha256(i_key_pad + message).digest()
        return hashlib.sha256(o_key_pad + inner_hash).digest()


    def _hkdf_extract(self, salt, ikm):
        """
        HKDF-Extract step.
        If salt is empty, use a string of HashLen zeros.
        """
        hash_len = hashlib.sha256().digest_size
        if salt is None or len(salt) == 0:
            salt = b'\x00' * hash_len
        return self._hmac_sha256(salt, ikm)


    def _hkdf_expand(self, prk, info, length):
        """
        HKDF-Expand step.
        'info' is optional context and application specific information (can be empty).
        """
        hash_len = hashlib.sha256().digest_size
        n = (length + hash_len - 1) // hash_len
        if n > 255:
            raise ValueError("Cannot expand to more than 255 * hash length bytes")
        t = b""
        okm = b""
        for i in range(1, n + 1):
            t = self._hmac_sha256(prk, t + info + bytes([i]))
            okm += t
        return okm[:length]
