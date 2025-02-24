import ucryptolib

class AESGCM:
    def __init__(self, key):
        self.key = key
        self._aes = ucryptolib.aes(key, 1)  # ECB mode
        self.H = self._encrypt_block(b'\x00' * 16)


    def encrypt(self, nonce, data, associated_data):
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes")
        # Compute J0 as specified in GCM for 96-bit IVs.
        J0 = nonce + b'\x00\x00\x00\x01'
        # Encryption uses counter blocks starting at inc32(J0)
        counter = self._inc32(J0)
        ciphertext = b""
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            keystream = self._encrypt_block(counter)
            ct_block = bytes(a ^ b for a, b in zip(block, keystream))
            ciphertext += ct_block
            counter = self._inc32(counter)
        S = self._ghash(associated_data, ciphertext)
        tag = bytes(a ^ b for a, b in zip(self._encrypt_block(J0), S))
        return ciphertext+tag


    def decrypt(self, nonce, data, associated_data):
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes")
        
        ciphertext, tag = data[:-16], data[-16:]

        J0 = nonce + b'\x00\x00\x00\x01'
        S = self._ghash(associated_data, ciphertext)
        computed_tag = bytes(a ^ b for a, b in zip(self._encrypt_block(J0), S))
        if computed_tag != tag:
            raise ValueError("Invalid tag! Authentication failed.")
        counter = self._inc32(J0)
        plaintext = b""
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            keystream = self._encrypt_block(counter)
            pt_block = bytes(a ^ b for a, b in zip(block, keystream))
            plaintext += pt_block
            counter = self._inc32(counter)
        return plaintext


    def _encrypt_block(self, block):
        if len(block) != 16:
            raise ValueError("Block must be 16 bytes")
        return self._aes.encrypt(block)


    def _gf_mult(self, X, Y):
        R = 0xe1000000000000000000000000000000
        Z = 0
        V = Y
        for i in range(128):
            if (X >> (127 - i)) & 1:
                Z ^= V
            if V & 1:
                V = (V >> 1) ^ R
            else:
                V >>= 1
        return Z


    def _ghash(self, aad, ciphertext):
        H_int = int.from_bytes(self.H, "big")
        X = 0

        # Process AAD
        for i in range(0, len(aad), 16):
            block = aad[i:i+16]
            if len(block) < 16:
                block += b'\x00' * (16 - len(block))
            X = self._gf_mult(X ^ int.from_bytes(block, "big"), H_int)

        # Process ciphertext
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            if len(block) < 16:
                block += b'\x00' * (16 - len(block))
            X = self._gf_mult(X ^ int.from_bytes(block, "big"), H_int)

        # Process length block: 64-bit lengths of AAD and ciphertext (in bits)
        aad_bits = len(aad) * 8
        ct_bits = len(ciphertext) * 8
        L = aad_bits.to_bytes(8, "big") + ct_bits.to_bytes(8, "big")
        X = self._gf_mult(X ^ int.from_bytes(L, "big"), H_int)

        return X.to_bytes(16, "big")


    def _inc32(self, block):
        counter = int.from_bytes(block[12:], "big")
        counter = (counter + 1) & 0xffffffff
        return block[:12] + counter.to_bytes(4, "big")
