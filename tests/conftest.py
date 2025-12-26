"""Pytest configuration and shared fixtures for PyTropicSquare tests.

This module provides:
- Mock classes for L1 transport layer
- Mock classes for cryptographic operations
- Shared test fixtures
- Common test utilities
"""

import pytest
from tropicsquare.exceptions import TropicSquareTimeoutError
from tropicsquare.constants.chip_status import CHIP_STATUS_READY


class MockL1Transport:
    """Mock L1 transport that returns predefined responses.

    This mock allows testing L2/L3 layers without actual hardware.
    Responses are provided as a list and returned sequentially.

    Attributes:
        responses (list): List of predefined responses to return
        requests_sent (list): History of all requests sent
        response_index (int): Current index in responses list
    """

    def __init__(self, responses=None):
        """Initialize mock transport.

        Args:
            responses: List of bytes to return from get_response() calls
        """
        self.responses = responses or []
        self.requests_sent = []
        self.response_index = 0

    def send_request(self, request_data):
        """Mock send_request - stores request and returns READY status.

        Args:
            request_data: Request bytes to send

        Returns:
            CHIP_STATUS_READY constant
        """
        self.requests_sent.append(request_data)
        return CHIP_STATUS_READY

    def get_response(self):
        """Mock get_response - returns next predefined response.

        Returns:
            Next response from responses list

        Raises:
            TropicSquareTimeoutError: If no more responses available
        """
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        raise TropicSquareTimeoutError("No more mock responses available")

    def _transfer(self, tx_data):
        """Mock SPI transfer - returns dummy data with READY status.

        Args:
            tx_data: Data to transfer

        Returns:
            Dummy response with READY status
        """
        return bytes([CHIP_STATUS_READY]) + b'\x00' * (len(tx_data) - 1)

    def _read(self, length):
        """Mock SPI read - returns zeros.

        Args:
            length: Number of bytes to read

        Returns:
            Zeros of specified length
        """
        return b'\x00' * length

    def _cs_low(self):
        """Mock chip select low - does nothing."""
        pass

    def _cs_high(self):
        """Mock chip select high - does nothing."""
        pass


class MockAESGCM:
    """Mock AES-GCM cipher for testing encrypted operations.

    This mock provides deterministic encryption/decryption for testing
    without requiring actual cryptographic operations.
    """

    def encrypt(self, nonce, data, associated_data):
        """Mock encryption - returns data with fixed tag.

        Args:
            nonce: 12-byte nonce
            data: Plaintext data
            associated_data: Additional authenticated data

        Returns:
            data + 16-byte authentication tag
        """
        # Return data with fixed 16-byte tag
        return data + b'\x00' * 16

    def decrypt(self, nonce, data, associated_data):
        """Mock decryption - removes tag from data.

        Args:
            nonce: 12-byte nonce
            data: Ciphertext with tag
            associated_data: Additional authenticated data

        Returns:
            data without last 16 bytes (tag)
        """
        # Remove last 16 bytes (tag)
        return data[:-16]


class MockCrypto:
    """Mock cryptographic operations for testing secure session.

    Provides deterministic outputs for all crypto operations to enable
    testing of session establishment without actual cryptography.
    """

    @staticmethod
    def mock_get_ephemeral_keypair():
        """Mock ephemeral key generation.

        Returns:
            Tuple of (private_key, public_key) with fixed test values
        """
        return (b'\x01' * 32, b'\x02' * 32)

    @staticmethod
    def mock_x25519_exchange(private_key, public_key):
        """Mock X25519 key exchange.

        Args:
            private_key: 32-byte private key
            public_key: 32-byte public key

        Returns:
            Fixed 32-byte shared secret
        """
        return b'\x03' * 32

    @staticmethod
    def mock_hkdf(salt, ikm, count=1):
        """Mock HKDF key derivation.

        Args:
            salt: Salt value
            ikm: Input keying material
            count: Number of keys to derive

        Returns:
            Single 32-byte key if count=1, otherwise list of keys
        """
        if count == 1:
            return b'\x04' * 32
        return [bytes([i] * 32) for i in range(4, 4 + count)]

    @staticmethod
    def mock_aesgcm(key):
        """Mock AES-GCM cipher creation.

        Args:
            key: 32-byte encryption key

        Returns:
            MockAESGCM instance
        """
        return MockAESGCM()


# Pytest fixtures

@pytest.fixture
def mock_transport():
    """Provide a mock L1 transport for testing.

    Returns:
        MockL1Transport instance
    """
    return MockL1Transport()


@pytest.fixture
def mock_crypto():
    """Provide mock crypto operations for testing.

    Returns:
        MockCrypto instance
    """
    return MockCrypto()
