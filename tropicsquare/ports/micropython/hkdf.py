from hashlib import sha256

class HKDF:

    @classmethod
    def derive(cls, salt, key_material, length = 32):
        prk = cls._hkdf_extract(salt, key_material)
        return cls._hkdf_expand(prk, b'', length)


    @classmethod
    def _hkdf_extract(cls, salt, ikm):
        """
        HKDF-Extract step.
        If salt is empty, use a string of HashLen zeros.
        """
        hash_len = 32 # Hard coded for SHA-256
        if salt is None or len(salt) == 0:
            salt = b'\x00' * hash_len
        return cls._hmac_sha256(salt, ikm)


    @classmethod
    def _hkdf_expand(cls, prk, info, length):
        """
        HKDF-Expand step.
        'info' is optional context and application specific information (can be empty).
        """
        hash_len = 32 # Hard coded for SHA-256
        n = (length + hash_len - 1) // hash_len
        if n > 255:
            raise ValueError("Cannot expand to more than 255 * hash length bytes")
        t = b""
        okm = b""
        for i in range(1, n + 1):
            t = cls._hmac_sha256(prk, t + info + bytes([i]))
            okm += t
        return okm[:length]


    @classmethod
    def _hmac_sha256(cls, key, message):
        blocksize = 64

        if len(key) > blocksize:
            key = sha256(key).digest()

        # Pad key with zeros if it's shorter than blocksize
        if len(key) < blocksize:
            key = key + b'\x00' * (blocksize - len(key))

        # Create inner and outer padded keys
        o_key_pad = bytes([b ^ 0x5c for b in key])
        i_key_pad = bytes([b ^ 0x36 for b in key])
        inner_hash = sha256(i_key_pad + message).digest()
        return sha256(o_key_pad + inner_hash).digest()
