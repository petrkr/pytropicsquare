"""ECC operations module for TROPIC01 secure element.

This module provides structured classes for ECC key information
and signature objects, replacing the tuple-based API.

Main exports:
    - EccKeyInfo: Information about keys in secure slots
    - EcdsaSignature: ECDSA signature from P256 curve
    - EddsaSignature: EdDSA signature from Ed25519 curve

Example::

    from tropicsquare import TropicSquare
    from tropicsquare.ecc import EccKeyInfo, EcdsaSignature
    from tropicsquare.constants.ecc import ECC_CURVE_ED25519

    ts = TropicSquare(transport)
    ts.start_secure_session(...)

    # Read key information
    key_info = ts.ecc_key_read(0)
    if key_info.curve == ECC_CURVE_ED25519:
        print("Ed25519 key")
    print(key_info.public_key.hex())

    # Create signature
    signature = ts.ecdsa_sign(1, message_hash)
    print(signature.r.hex())
"""

"""ECC key information data structure."""

from tropicsquare.constants.ecc import ECC_CURVE_P256, ECC_CURVE_ED25519


class EccKeyInfo:
    """ECC key information from secure key slot.

    Represents the public key and metadata stored in a TROPIC01 ECC key slot,
    as returned by ecc_key_read().

    :param curve: Curve type (ECC_CURVE_P256 or ECC_CURVE_ED25519)
    :param origin: Key origin (ECC_KEY_ORIGIN_GENERATED or ECC_KEY_ORIGIN_STORED)
    :param public_key: Public key bytes (32 or 64 bytes depending on curve)

    Example::

        key_info = ts.ecc_key_read(0)
        if key_info.curve == ECC_CURVE_ED25519:
            print("Ed25519 key")
        print(key_info.public_key.hex())
    """

    def __init__(self, curve: int, origin: int, public_key: bytes):
        """Initialize ECC key information.

        :param curve: Curve type constant
        :param origin: Key origin constant
        :param public_key: Public key bytes
        """
        self.curve = curve
        self.origin = origin
        self.public_key = public_key

    def to_dict(self) -> dict:
        """Convert key information to dictionary.

        :returns: Dictionary with curve, origin, and public_key fields
        :rtype: dict

        Example::

            {
                'curve': 1,
                'origin': 0,
                'public_key': '04a1b2c3...'
            }
        """
        return {
            'curve': self.curve,
            'origin': self.origin,
            'public_key': self.public_key.hex()
        }

    def __str__(self) -> str:
        """Get human-readable string representation.

        :returns: Formatted string with key information
        """
        curve_name = "P256" if self.curve == ECC_CURVE_P256 else "Ed25519" if self.curve == ECC_CURVE_ED25519 else f"Unknown (0x{self.curve:02x})"
        return f"ECC Key: {curve_name}, Origin: {self.origin}, PubKey: {self.public_key.hex()[:32]}..."

    def __repr__(self) -> str:
        """Get detailed string representation for debugging.

        :returns: Detailed representation with class name and fields
        """
        return f"EccKeyInfo(curve=0x{self.curve:02x}, origin=0x{self.origin:02x}, pubkey={self.public_key.hex()[:16]}...)"
