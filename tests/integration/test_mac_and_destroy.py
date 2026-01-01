"""Integration tests for MAC_And_Destroy operations.

Tests atomic PIN verification functionality against TROPIC01 model server.

Based on libtropic reference: /home/petrkr/git/libtropic/tests/functional/lt_test_rev_mac_and_destroy.c
This is a simplified version focusing on API validation rather than full PIN workflow.
"""

import pytest
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)
from tropicsquare.constants import MAC_AND_DESTROY_DATA_SIZE

pytestmark = pytest.mark.integration


class TestMacAndDestroy:
    """Test MAC and Destroy operations."""

    def test_mac_and_destroy_basic(self, tropic_square):
        """Test basic MAC and destroy operation with 32-byte data."""
        # Start secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Test data - exactly 32 bytes as per API specification
        test_data = b"Test MAC and Destroy data 32B\x00\x00\x00"
        assert len(test_data) == MAC_AND_DESTROY_DATA_SIZE

        # Perform MAC and destroy on slot 0
        mac_result = tropic_square.mac_and_destroy(0, test_data)

        # Verify MAC result
        assert isinstance(mac_result, bytes)
        assert len(mac_result) == 32  # API spec: DATA_OUT is 32 bytes

    def test_mac_and_destroy_slot_independence(self, tropic_square):
        """Test that different slots produce different MACs."""
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        test_data = b"Slot independence test 32B__\x00\x00\x00\x00"
        assert len(test_data) == MAC_AND_DESTROY_DATA_SIZE

        # Compute MAC on different slots
        mac_slot0 = tropic_square.mac_and_destroy(0, test_data)
        mac_slot1 = tropic_square.mac_and_destroy(1, test_data)

        # Different slots should produce different MACs
        assert mac_slot0 != mac_slot1
