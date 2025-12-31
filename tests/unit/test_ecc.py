"""Tests for ECC module classes.

This module tests:
- EccKeyInfo: Key information from secure slots
- Signature: Base signature class
- EcdsaSignature: ECDSA signatures (P256)
- EddsaSignature: EdDSA signatures (Ed25519)
"""

import pytest
from tropicsquare.ecc import EccKeyInfo
from tropicsquare.ecc.signature import Signature, EcdsaSignature, EddsaSignature
from tropicsquare.constants.ecc import ECC_CURVE_P256, ECC_CURVE_ED25519


class TestEccKeyInfo:
    """Test EccKeyInfo class."""

    def test_init_with_p256_key(self):
        """Test initialization with P256 key."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=0, public_key=pubkey)
        assert key_info.curve == ECC_CURVE_P256
        assert key_info.origin == 0
        assert key_info.public_key == pubkey

    def test_init_with_ed25519_key(self):
        """Test initialization with Ed25519 key."""
        pubkey = bytes.fromhex('e5f6a7b8' * 8)
        key_info = EccKeyInfo(curve=ECC_CURVE_ED25519, origin=1, public_key=pubkey)
        assert key_info.curve == ECC_CURVE_ED25519
        assert key_info.origin == 1
        assert key_info.public_key == pubkey

    def test_curve_property(self):
        """Test curve property access."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=0, public_key=pubkey)
        assert key_info.curve == ECC_CURVE_P256

    def test_origin_property(self):
        """Test origin property access."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=1, public_key=pubkey)
        assert key_info.origin == 1

    def test_public_key_property(self):
        """Test public_key property access."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=0, public_key=pubkey)
        assert key_info.public_key == pubkey

    def test_to_dict(self):
        """Test to_dict() returns correct format."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=0, public_key=pubkey)
        result = key_info.to_dict()
        assert 'curve' in result
        assert 'origin' in result
        assert 'public_key' in result
        assert result['curve'] == ECC_CURVE_P256
        assert result['origin'] == 0
        assert result['public_key'] == pubkey.hex()

    def test_str_representation_p256(self):
        """Test __str__() for P256 key."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=0, public_key=pubkey)
        result = str(key_info)
        assert 'P256' in result
        assert 'ECC Key' in result

    def test_str_representation_ed25519(self):
        """Test __str__() for Ed25519 key."""
        pubkey = bytes.fromhex('e5f6a7b8' * 8)
        key_info = EccKeyInfo(curve=ECC_CURVE_ED25519, origin=0, public_key=pubkey)
        result = str(key_info)
        assert 'Ed25519' in result
        assert 'ECC Key' in result

    def test_repr_representation(self):
        """Test __repr__() representation."""
        pubkey = bytes.fromhex('04' + 'a1b2c3d4' * 16)
        key_info = EccKeyInfo(curve=ECC_CURVE_P256, origin=0, public_key=pubkey)
        result = repr(key_info)
        assert 'EccKeyInfo' in result
        assert 'curve' in result
        assert 'origin' in result


class TestSignature:
    """Test Signature base class."""

    def test_init(self):
        """Test basic initialization."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = Signature(r=r, s=s)
        assert sig.r == r
        assert sig.s == s

    def test_r_component(self):
        """Test R component storage."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = Signature(r=r, s=s)
        assert len(sig.r) == 32
        assert sig.r == r

    def test_s_component(self):
        """Test S component storage."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = Signature(r=r, s=s)
        assert len(sig.s) == 32
        assert sig.s == s

    def test_to_dict(self):
        """Test to_dict() returns hex-encoded components."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = Signature(r=r, s=s)
        result = sig.to_dict()
        assert 'r' in result
        assert 's' in result
        assert result['r'] == r.hex()
        assert result['s'] == s.hex()

    def test_str_representation(self):
        """Test __str__() formatting."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = Signature(r=r, s=s)
        result = str(sig)
        assert 'Signature' in result
        assert 'R:' in result
        assert 'S:' in result

    def test_repr_representation(self):
        """Test __repr__() representation."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = Signature(r=r, s=s)
        result = repr(sig)
        assert 'Signature' in result
        assert 'r=' in result
        assert 's=' in result


class TestEcdsaSignature:
    """Test EcdsaSignature class."""

    def test_inherits_from_signature(self):
        """Test that EcdsaSignature inherits from Signature."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EcdsaSignature(r=r, s=s)
        assert isinstance(sig, Signature)

    def test_init(self):
        """Test initialization."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EcdsaSignature(r=r, s=s)
        assert sig.r == r
        assert sig.s == s

    def test_to_dict(self):
        """Test to_dict() (inherited from Signature)."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EcdsaSignature(r=r, s=s)
        result = sig.to_dict()
        assert 'r' in result
        assert 's' in result
        assert result['r'] == r.hex()
        assert result['s'] == s.hex()

    def test_str_shows_class_name(self):
        """Test __str__() contains 'EcdsaSignature'."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EcdsaSignature(r=r, s=s)
        result = str(sig)
        assert 'EcdsaSignature' in result
        assert 'R:' in result
        assert 'S:' in result

    def test_repr_shows_class_name(self):
        """Test __repr__() contains 'EcdsaSignature'."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EcdsaSignature(r=r, s=s)
        result = repr(sig)
        assert 'EcdsaSignature' in result


class TestEddsaSignature:
    """Test EddsaSignature class."""

    def test_inherits_from_signature(self):
        """Test that EddsaSignature inherits from Signature."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EddsaSignature(r=r, s=s)
        assert isinstance(sig, Signature)

    def test_init(self):
        """Test initialization."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EddsaSignature(r=r, s=s)
        assert sig.r == r
        assert sig.s == s

    def test_to_dict(self):
        """Test to_dict() (inherited from Signature)."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EddsaSignature(r=r, s=s)
        result = sig.to_dict()
        assert 'r' in result
        assert 's' in result
        assert result['r'] == r.hex()
        assert result['s'] == s.hex()

    def test_str_shows_class_name(self):
        """Test __str__() contains 'EddsaSignature'."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EddsaSignature(r=r, s=s)
        result = str(sig)
        assert 'EddsaSignature' in result
        assert 'R:' in result
        assert 'S:' in result

    def test_repr_shows_class_name(self):
        """Test __repr__() contains 'EddsaSignature'."""
        r = bytes.fromhex('12345678' * 8)
        s = bytes.fromhex('abcdef01' * 8)
        sig = EddsaSignature(r=r, s=s)
        result = repr(sig)
        assert 'EddsaSignature' in result
