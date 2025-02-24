
class X25519:
    @classmethod
    def exchange(cls, private_bytes, public_bytes):
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


    @classmethod
    def pubkey(cls, private_bytes):
        # The base point for X25519 is 9, represented as a 32-byte little-endian value.
        basepoint = (9).to_bytes(32, "little")
        return cls.exchange(private_bytes, basepoint)
