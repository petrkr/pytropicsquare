"""L3 encrypted command tests.

Tests for L3 protocol layer commands requiring encrypted session.
These tests verify L3 command execution (random generation, etc.)
using TCP transport connection to the TROPIC01 model server.

All tests in this file establish their own secure session for isolation.
"""

import pytest
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestRandomGeneration:
    """Test random number generation via L3 commands."""

    def test_random_generation(self, tropic_square):
        """Test random number generation.

        :param tropic_square: TropicSquare instance fixture
        """
        # Establish session
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )

        # Generate random bytes
        random_data = tropic_square.get_random(32)

        assert random_data is not None
        assert isinstance(random_data, bytes)
        assert len(random_data) == 32

        # Generate again - should be different
        random_data2 = tropic_square.get_random(32)
        assert random_data != random_data2, "RNG returned same value twice"
