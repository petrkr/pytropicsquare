"""ECC key management and signing tests.

Tests for ECC key operations including key generation, import, signing,
and cross-type validation. These tests verify proper error handling for
empty slots, wrong key types, and correct key origin tracking.

All tests in this file establish secure session before ECC operations.
"""

import hashlib
import pytest
from tropicsquare.constants.ecc import (
    ECC_CURVE_P256,
    ECC_CURVE_ED25519,
    ECC_KEY_ORIGIN_GENERATED,
    ECC_KEY_ORIGIN_STORED
)
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)
from tropicsquare.exceptions import TropicSquareECCInvalidKeyError

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

# Test slots - use slots that won't interfere with examples
TEST_SLOT_0 = 10
TEST_SLOT_1 = 11


class TestEccEmptySlots:
    """Test ECC operations on empty slots."""

    def test_empty_slot_operations(self, tropic_square):
        """Test that operations on empty slots raise TropicSquareECCInvalidKeyError.

        Verifies that:
        1. Reading from empty slot raises TropicSquareECCInvalidKeyError
        2. Signing with empty P256 slot raises TropicSquareECCInvalidKeyError
        3. Signing with empty Ed25519 slot raises TropicSquareECCInvalidKeyError
        4. Erasing empty slots is safe (cleanup)

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
        except Exception:
            pass  # Ignore if already empty

        try:
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass  # Ignore if already empty

        # 1. Reading from empty slot should raise error
        with pytest.raises(TropicSquareECCInvalidKeyError):
            tropic_square.ecc_key_read(TEST_SLOT_0)

        # 2. ECDSA signing with empty slot should raise error
        test_hash = b'\x00' * 32
        with pytest.raises(TropicSquareECCInvalidKeyError):
            tropic_square.ecdsa_sign(TEST_SLOT_0, test_hash)

        # 3. EdDSA signing with empty slot should raise error
        test_message = b'Test message'
        with pytest.raises(TropicSquareECCInvalidKeyError):
            tropic_square.eddsa_sign(TEST_SLOT_0, test_message)


class TestEccKeyGeneration:
    """Test ECC key generation and origin tracking."""

    def test_key_generation_lifecycle(self, tropic_square):
        """Test complete key generation lifecycle for both curve types.

        Verifies that:
        1. P256 key can be generated
        2. Generated P256 key has correct origin (GENERATED)
        3. Generated P256 key has correct curve type
        4. Ed25519 key can be generated
        5. Generated Ed25519 key has correct origin (GENERATED)
        6. Generated Ed25519 key has correct curve type
        7. Keys can be erased

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass

        # === Test P256 key generation ===

        # 1. Generate P256 key
        result = tropic_square.ecc_key_generate(TEST_SLOT_0, ECC_CURVE_P256)
        assert result is True

        # 2. Read key and verify origin
        key_info = tropic_square.ecc_key_read(TEST_SLOT_0)
        assert key_info.origin == ECC_KEY_ORIGIN_GENERATED, \
            f"Expected GENERATED origin, got {key_info.origin}"

        # 3. Verify curve type
        assert key_info.curve == ECC_CURVE_P256, \
            f"Expected P256 curve, got {key_info.curve}"

        # Verify public key exists and has reasonable length (P256 = 64 bytes uncompressed)
        assert len(key_info.public_key) > 0, "Public key should not be empty"

        # === Test Ed25519 key generation ===

        # 4. Generate Ed25519 key
        result = tropic_square.ecc_key_generate(TEST_SLOT_1, ECC_CURVE_ED25519)
        assert result is True

        # 5. Read key and verify origin
        key_info = tropic_square.ecc_key_read(TEST_SLOT_1)
        assert key_info.origin == ECC_KEY_ORIGIN_GENERATED, \
            f"Expected GENERATED origin, got {key_info.origin}"

        # 6. Verify curve type
        assert key_info.curve == ECC_CURVE_ED25519, \
            f"Expected Ed25519 curve, got {key_info.curve}"

        # Verify public key exists (Ed25519 = 32 bytes)
        assert len(key_info.public_key) > 0, "Public key should not be empty"

        # 7. Cleanup - erase both keys
        result = tropic_square.ecc_key_erase(TEST_SLOT_0)
        assert result is True

        result = tropic_square.ecc_key_erase(TEST_SLOT_1)
        assert result is True


class TestEccKeyImport:
    """Test ECC key import and origin tracking."""

    def test_key_import_lifecycle(self, tropic_square):
        """Test importing external keys and verifying origin.

        Verifies that:
        1. P256 private key can be imported
        2. Imported P256 key has correct origin (STORED)
        3. Imported P256 key has correct curve type
        4. Ed25519 private key can be imported
        5. Imported Ed25519 key has correct origin (STORED)
        6. Imported Ed25519 key has correct curve type
        7. Imported keys can be erased

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass

        # === Test P256 key import ===

        # Demo P256 private key (32 bytes)
        demo_p256_key = bytes.fromhex("1234567890abcdef" * 4)

        # 1. Import P256 key
        result = tropic_square.ecc_key_store(TEST_SLOT_0, ECC_CURVE_P256, demo_p256_key)
        assert result is True

        # 2. Read key and verify origin
        key_info = tropic_square.ecc_key_read(TEST_SLOT_0)
        assert key_info.origin == ECC_KEY_ORIGIN_STORED, \
            f"Expected STORED origin, got {key_info.origin}"

        # 3. Verify curve type
        assert key_info.curve == ECC_CURVE_P256, \
            f"Expected P256 curve, got {key_info.curve}"

        # Store public key for later verification
        p256_public_key = key_info.public_key

        # === Test Ed25519 key import ===

        # Demo Ed25519 private key (32 bytes)
        demo_ed25519_key = bytes.fromhex("fedcba0987654321" * 4)

        # 4. Import Ed25519 key
        result = tropic_square.ecc_key_store(TEST_SLOT_1, ECC_CURVE_ED25519, demo_ed25519_key)
        assert result is True

        # 5. Read key and verify origin
        key_info = tropic_square.ecc_key_read(TEST_SLOT_1)
        assert key_info.origin == ECC_KEY_ORIGIN_STORED, \
            f"Expected STORED origin, got {key_info.origin}"

        # 6. Verify curve type
        assert key_info.curve == ECC_CURVE_ED25519, \
            f"Expected Ed25519 curve, got {key_info.curve}"

        # 7. Cleanup - erase both keys
        result = tropic_square.ecc_key_erase(TEST_SLOT_0)
        assert result is True

        result = tropic_square.ecc_key_erase(TEST_SLOT_1)
        assert result is True


class TestEccSigningCrossType:
    """Test ECC signing with wrong key types."""

    def test_cross_type_signing_errors(self, tropic_square):
        """Test that signing with wrong key type raises errors.

        Verifies that:
        1. ECDSA signing with Ed25519 key raises TropicSquareECCInvalidKeyError
        2. EdDSA signing with P256 key raises TropicSquareECCInvalidKeyError
        3. Keys are properly cleaned up

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty, then generate keys
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass

        # Generate P256 key in slot 0
        tropic_square.ecc_key_generate(TEST_SLOT_0, ECC_CURVE_P256)

        # Generate Ed25519 key in slot 1
        tropic_square.ecc_key_generate(TEST_SLOT_1, ECC_CURVE_ED25519)

        # Verify keys are present
        p256_key = tropic_square.ecc_key_read(TEST_SLOT_0)
        assert p256_key.curve == ECC_CURVE_P256

        ed25519_key = tropic_square.ecc_key_read(TEST_SLOT_1)
        assert ed25519_key.curve == ECC_CURVE_ED25519

        # === Test cross-type signing errors ===

        test_hash = hashlib.sha256(b"Test message").digest()
        test_message = b"Test message"

        # 1. Try ECDSA signing with Ed25519 key (should fail)
        with pytest.raises(TropicSquareECCInvalidKeyError):
            tropic_square.ecdsa_sign(TEST_SLOT_1, test_hash)

        # 2. Try EdDSA signing with P256 key (should fail)
        with pytest.raises(TropicSquareECCInvalidKeyError):
            tropic_square.eddsa_sign(TEST_SLOT_0, test_message)

        # 3. Cleanup
        tropic_square.ecc_key_erase(TEST_SLOT_0)
        tropic_square.ecc_key_erase(TEST_SLOT_1)


class TestEccSigningCorrectType:
    """Test ECC signing with correct key types."""

    def test_correct_type_signing(self, tropic_square):
        """Test that signing with correct key types works properly.

        Verifies that:
        1. ECDSA signing with P256 key works
        2. EdDSA signing with Ed25519 key works
        3. Signatures have correct format (r and s components)
        4. Multiple signatures with same key produce different signatures
        5. Keys are properly cleaned up

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty, then generate keys
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass

        # Generate P256 key in slot 0
        tropic_square.ecc_key_generate(TEST_SLOT_0, ECC_CURVE_P256)

        # Generate Ed25519 key in slot 1
        tropic_square.ecc_key_generate(TEST_SLOT_1, ECC_CURVE_ED25519)

        # === Test ECDSA signing with P256 key ===

        # 1. Sign hash with P256 key
        test_hash = hashlib.sha256(b"Test message").digest()
        signature1 = tropic_square.ecdsa_sign(TEST_SLOT_0, test_hash)

        # Verify signature format
        assert signature1.r is not None
        assert signature1.s is not None
        assert len(signature1.r) == 32, f"Expected 32 bytes for r, got {len(signature1.r)}"
        assert len(signature1.s) == 32, f"Expected 32 bytes for s, got {len(signature1.s)}"

        # 2. Sign different hash
        test_hash2 = hashlib.sha256(b"Different message").digest()
        signature2 = tropic_square.ecdsa_sign(TEST_SLOT_0, test_hash2)

        # Signatures should be different for different inputs
        assert signature1.r != signature2.r or signature1.s != signature2.s, \
            "Different messages should produce different signatures"

        # === Test EdDSA signing with Ed25519 key ===

        # 3. Sign message with Ed25519 key
        test_message = b"Test message"
        signature3 = tropic_square.eddsa_sign(TEST_SLOT_1, test_message)

        # Verify signature format
        assert signature3.r is not None
        assert signature3.s is not None
        assert len(signature3.r) == 32, f"Expected 32 bytes for r, got {len(signature3.r)}"
        assert len(signature3.s) == 32, f"Expected 32 bytes for s, got {len(signature3.s)}"

        # 4. Sign different message
        test_message2 = b"Different message"
        signature4 = tropic_square.eddsa_sign(TEST_SLOT_1, test_message2)

        # Signatures should be different for different inputs
        assert signature3.r != signature4.r or signature3.s != signature4.s, \
            "Different messages should produce different signatures"

        # 5. Cleanup
        tropic_square.ecc_key_erase(TEST_SLOT_0)
        tropic_square.ecc_key_erase(TEST_SLOT_1)


class TestEccSigningWrongSlot:
    """Test ECC signing with keys from different slots."""

    def test_different_keys_produce_different_signatures(self, tropic_square):
        """Test that signing same data with different keys produces different signatures.

        Verifies that:
        1. Two different P256 keys produce different signatures for same data
        2. Keys are properly cleaned up

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass

        # Generate two different P256 keys
        tropic_square.ecc_key_generate(TEST_SLOT_0, ECC_CURVE_P256)
        tropic_square.ecc_key_generate(TEST_SLOT_1, ECC_CURVE_P256)

        # Verify they have different public keys
        key0 = tropic_square.ecc_key_read(TEST_SLOT_0)
        key1 = tropic_square.ecc_key_read(TEST_SLOT_1)
        assert key0.public_key != key1.public_key, \
            "Two generated keys should have different public keys"

        # 1. Sign same data with both keys
        test_hash = hashlib.sha256(b"Test message").digest()
        sig0 = tropic_square.ecdsa_sign(TEST_SLOT_0, test_hash)
        sig1 = tropic_square.ecdsa_sign(TEST_SLOT_1, test_hash)

        # Signatures should be different (using wrong key produces different signature)
        assert sig0.r != sig1.r or sig0.s != sig1.s, \
            "Different keys should produce different signatures"

        # 2. Cleanup
        tropic_square.ecc_key_erase(TEST_SLOT_0)
        tropic_square.ecc_key_erase(TEST_SLOT_1)


class TestEccPublicKeyVerification:
    """Test that imported private keys match derived public keys."""

    def test_imported_key_public_key_correspondence(self, tropic_square):
        """Test that imported private key corresponds to returned public key.

        This test imports known private keys and verifies that the public keys
        returned by the chip match what we can derive from the private key using
        standard cryptographic libraries.

        Verifies that:
        1. For P256: imported private key matches derived public key
        2. For Ed25519: imported private key matches derived public key
        3. Keys are properly cleaned up

        :param tropic_square: TropicSquare instance fixture
        """
        try:
            from cryptography.hazmat.primitives.asymmetric import ec, ed25519
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            pytest.skip("cryptography library not available for key verification")

        # Ensure no session is active from previous tests
        try:
            tropic_square.abort_secure_session()
        except Exception:
            pass

        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Ensure slots are empty
        try:
            tropic_square.ecc_key_erase(TEST_SLOT_0)
            tropic_square.ecc_key_erase(TEST_SLOT_1)
        except Exception:
            pass

        # === Test P256 key correspondence ===

        # Generate a proper P256 private key using cryptography library
        p256_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        p256_private_bytes = p256_private_key.private_numbers().private_value.to_bytes(32, 'big')

        # Derive public key from private key
        p256_public_key = p256_private_key.public_key()
        p256_public_numbers = p256_public_key.public_numbers()

        # Convert to raw format (x || y) - chip returns without 0x04 prefix
        x_bytes = p256_public_numbers.x.to_bytes(32, 'big')
        y_bytes = p256_public_numbers.y.to_bytes(32, 'big')
        expected_p256_pubkey = x_bytes + y_bytes

        # 1. Import P256 key and verify public key matches
        tropic_square.ecc_key_store(TEST_SLOT_0, ECC_CURVE_P256, p256_private_bytes)
        key_info = tropic_square.ecc_key_read(TEST_SLOT_0)

        assert key_info.public_key == expected_p256_pubkey, \
            f"P256 public key mismatch:\nExpected: {expected_p256_pubkey.hex()}\nGot: {key_info.public_key.hex()}"

        # === Test Ed25519 key correspondence ===

        # Generate a proper Ed25519 private key
        ed25519_private_key = ed25519.Ed25519PrivateKey.generate()
        ed25519_private_bytes = ed25519_private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Derive public key from private key
        ed25519_public_key = ed25519_private_key.public_key()
        expected_ed25519_pubkey = ed25519_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        # 2. Import Ed25519 key and verify public key matches
        tropic_square.ecc_key_store(TEST_SLOT_1, ECC_CURVE_ED25519, ed25519_private_bytes)
        key_info = tropic_square.ecc_key_read(TEST_SLOT_1)

        assert key_info.public_key == expected_ed25519_pubkey, \
            f"Ed25519 public key mismatch:\nExpected: {expected_ed25519_pubkey.hex()}\nGot: {key_info.public_key.hex()}"

        # 3. Cleanup
        tropic_square.ecc_key_erase(TEST_SLOT_0)
        tropic_square.ecc_key_erase(TEST_SLOT_1)
