"""Secure session establishment tests.

Tests for secure session management and encrypted communication.
These tests verify session establishment with factory pairing keys
and encrypted command execution using TCP transport connection
to the TROPIC01 model server.

All tests in this file establish secure session before executing commands.
"""

import pytest
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0
)
from tropicsquare.exceptions import TropicSquareNoSession

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestSessionLifecycle:
    """Test secure session lifecycle (start/abort)."""

    def test_session_lifecycle(self, tropic_square):
        """Test complete session lifecycle with ping verification.

        Verifies that:
        1. Ping fails without session (TropicSquareNoSession)
        2. Session can be established
        3. Ping works during active session with multiple test vectors
        4. Session can be aborted
        5. Ping fails again after abort (TropicSquareNoSession)

        :param tropic_square: TropicSquare instance fixture
        """

        test_data = b'Test ping data!!'

        # Ensure no session is active from previous tests
        # (tropic_square fixture is session-scoped, shared across tests)
        try:
            tropic_square.abort_secure_session()
        except Exception:
            pass  # Ignore if no session was active

        # 1. Ping should fail without session
        with pytest.raises(TropicSquareNoSession):
            tropic_square.ping(test_data)

        # 2. Establish session
        result = tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0
        )
        assert result is True

        # 3. Ping should work with active session - test with multiple vectors
        test_vectors = [
            b'\x00' * 16,
            b'\xFF' * 16,
            bytes(range(16)),
            b'Hello, TROPIC01!',
        ]

        for data in test_vectors:
            response = tropic_square.ping(data)
            assert response == data, f"Ping echo mismatch for {data.hex()}"

        # 4. Abort session
        result = tropic_square.abort_secure_session()
        assert result is True

        # 5. Ping should fail again after abort
        with pytest.raises(TropicSquareNoSession):
            tropic_square.ping(test_data)
