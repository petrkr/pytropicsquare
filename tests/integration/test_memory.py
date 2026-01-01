"""Memory operations tests.

Tests for memory read/write operations.
These tests verify data slot operations using TCP transport
connection to the TROPIC01 model server.

All tests in this file establish secure session before memory operations.
"""

import pytest
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestMemoryOperations:
    """Test memory slot lifecycle operations."""

    def test_memory_slot_lifecycle(self, tropic_square):
        """Test complete memory slot lifecycle.

        Verifies that:
        1. Erase slot to ensure clean state
        2. Reading empty slot returns empty data
        3. Erasing empty slot succeeds (idempotent operation)
        4. Writing to slot succeeds
        5. Reading from slot returns correct data
        6. Erasing slot succeeds
        7. Reading erased slot returns empty data again

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish secure session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        slot_id = 0
        test_data = b"Test data for memory slot"

        # 1. Erase slot to ensure clean state
        result = tropic_square.mem_data_erase(slot_id)
        assert result is True

        # 2. Reading empty slot should return empty data
        read_data = tropic_square.mem_data_read(slot_id)
        assert read_data == b'', f"Expected empty slot to return b'', got {read_data!r}"

        # 3. Erasing empty slot should succeed (idempotent)
        result = tropic_square.mem_data_erase(slot_id)
        assert result is True

        # 4. Write to slot
        result = tropic_square.mem_data_write(test_data, slot_id)
        assert result is True

        # 5. Read from slot - should return correct data
        read_data = tropic_square.mem_data_read(slot_id)
        assert read_data == test_data

        # 6. Erase slot
        result = tropic_square.mem_data_erase(slot_id)
        assert result is True

        # 7. Reading erased slot should return empty data again
        read_data = tropic_square.mem_data_read(slot_id)
        assert read_data == b'', f"Expected erased slot to return b'', got {read_data!r}"
