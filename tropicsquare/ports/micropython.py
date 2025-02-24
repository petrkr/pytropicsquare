import hashlib
from random import getrandbits

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


    def _get_ephemeral_keypair(self):
        ehpriv = b''
        for _ in range(8):
            ehpriv += getrandbits(32).to_bytes(4, "big")

        return (ehpriv, self._x25519_pubkey(ehpriv))


    def _hkdf(self, salt, shared_secret, length = 1):
        prk = self._hkdf_extract(salt, shared_secret)
        result = self._hkdf_expand(prk, b'', length * 32)

        if length > 1:
            return [result[i*32:(i+1)*32] for i in range(length)]
        else:
            return result


    def _x25519_exchange(self, private_bytes, public_bytes):
        if len(private_bytes) != 32 or len(public_bytes) != 32:
            raise ValueError("Both private and public keys must be 32 bytes long")

        # Clamp the private key per RFC 7748:
        k = bytearray(private_bytes)
        k[0] &= 248
        k[31] &= 127
        k[31] |= 64
        scalar = int.from_bytes(k, "little")
        u = int.from_bytes(public_bytes, "little")

        # Curve25519 prime and constant:
        p = 2**255 - 19
        a24 = 121665  # (486662 - 2) // 4

        # Set up ladder variables:
        x1 = u
        x2, z2 = 1, 0
        x3, z3 = u, 1
        swap = 0

        # Loop over bits of the scalar, from bit 254 down to bit 0.
        for t in range(254, -1, -1):
            k_t = (scalar >> t) & 1
            swap ^= k_t
            # Conditional swap: if swap is 1, swap (x2,z2) with (x3,z3)
            if swap:
                x2, x3 = x3, x2
                z2, z3 = z3, z2
            swap = k_t

            # Montgomery ladder step:
            A = (x2 + z2) % p
            AA = (A * A) % p
            B = (x2 - z2) % p
            BB = (B * B) % p
            E = (AA - BB) % p
            C = (x3 + z3) % p
            D = (x3 - z3) % p
            DA = (D * A) % p
            CB = (C * B) % p

            # Update x3 and z3:
            x3 = (DA + CB) % p
            x3 = (x3 * x3) % p
            z3 = (DA - CB) % p
            z3 = (z3 * z3) % p
            z3 = (x1 * z3) % p

            # Update x2 and z2:
            x2 = (AA * BB) % p
            z2 = (E * (AA + a24 * E)) % p

        # Final conditional swap if needed:
        if swap:
            x2, x3 = x3, x2
            z2, z3 = z3, z2

        # Compute the shared secret as x2/z2 mod p:
        z2_inv = pow(z2, p - 2, p)
        shared_secret = (x2 * z2_inv) % p

        # Return the result as 32-byte little-endian bytes:
        return shared_secret.to_bytes(32, "little")


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


    def _x25519_pubkey(self, private_bytes):
        # The base point for X25519 is 9, represented as a 32-byte little-endian value.
        basepoint = (9).to_bytes(32, "little")
        return self._x25519_exchange(private_bytes, basepoint)
