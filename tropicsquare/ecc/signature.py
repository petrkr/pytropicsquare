"""Signature classes for TROPIC01 ECC signing operations."""


class Signature:
    """Base class for cryptographic signatures.

    Represents a digital signature with R and S components as returned
    by TROPIC01 signing operations (ECDSA and EdDSA).

    :param r: R component of signature (32 bytes)
    :param s: S component of signature (32 bytes)
    """

    def __init__(self, r: bytes, s: bytes):
        """Initialize signature.

        :param r: R component (32 bytes)
        :param s: S component (32 bytes)
        """
        self.r = r
        self.s = s

    def to_dict(self) -> dict:
        """Convert signature to dictionary.

        :returns: Dictionary with R and S components
        :rtype: dict

        Example::

            {
                'r': 'a1b2c3...',
                's': 'd4e5f6...'
            }
        """
        return {
            'r': self.r.hex(),
            's': self.s.hex()
        }

    def __str__(self) -> str:
        """Get human-readable string representation.

        :returns: Formatted signature with R and S components
        """
        return f"{self.__class__.__name__}:\n  R: {self.r.hex()}\n  S: {self.s.hex()}"

    def __repr__(self) -> str:
        """Get detailed string representation for debugging.

        :returns: Detailed representation with class name
        """
        return f"{self.__class__.__name__}(r={self.r.hex()[:16]}..., s={self.s.hex()[:16]}...)"


class EcdsaSignature(Signature):
    """ECDSA signature from P256 curve signing operation.

    Represents an ECDSA (Elliptic Curve Digital Signature Algorithm)
    signature created using the P256 curve. This signature can be verified
    using standard ECDSA verification with the corresponding public key.

    The signature consists of two 32-byte components (R, S) that can be
    converted to DER encoding for use with standard cryptographic libraries.

    Example::

        signature = ts.ecdsa_sign(1, message_hash)
        print(signature.r.hex())
        print(signature.s.hex())
    """


class EddsaSignature(Signature):
    """EdDSA signature from Ed25519 curve signing operation.

    Represents an EdDSA (Edwards-curve Digital Signature Algorithm)
    signature created using the Ed25519 curve. This signature can be verified
    using standard Ed25519 verification with the corresponding public key.

    The signature consists of two 32-byte components (R, S) that form
    the standard 64-byte Ed25519 signature format when concatenated.

    Example::

        signature = ts.eddsa_sign(0, message)
        print(signature.r.hex())
        print(signature.s.hex())
    """
