"""Pairing key integration tests against TROPIC01 model server."""

import pytest
from tropicsquare.constants import PAIRING_KEY_MAX
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0,
)


pytestmark = pytest.mark.integration


class TestPairingKeys:
    """Test pairing key API behavior on model."""

    def test_pairing_key_read_factory_slot(self, tropic_square):
        """Factory slot 0 should contain expected public key from model config."""
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0,
        )

        key = tropic_square.pairing_key_read(FACTORY_PAIRING_KEY_INDEX)

        assert isinstance(key, bytes)
        assert len(key) == 32
        assert key == FACTORY_PAIRING_PUBLIC_KEY_PROD0

    @pytest.mark.parametrize("slot", [-1, PAIRING_KEY_MAX + 1])
    def test_pairing_slot_range_validation(self, tropic_square, slot):
        """Pairing slot index must stay within 0..PAIRING_KEY_MAX."""
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0,
        )

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            tropic_square.pairing_key_read(slot)

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            tropic_square.pairing_key_write(slot, b"\x01" * 32)

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            tropic_square.pairing_key_invalidate(slot)

    def test_pairing_key_write_length_validation(self, tropic_square):
        """Pairing key write requires exactly 32 bytes."""
        tropic_square.start_secure_session(
            FACTORY_PAIRING_KEY_INDEX,
            FACTORY_PAIRING_PRIVATE_KEY_PROD0,
            FACTORY_PAIRING_PUBLIC_KEY_PROD0,
        )

        with pytest.raises(ValueError, match=r"Key must be exactly 32 bytes"):
            tropic_square.pairing_key_write(FACTORY_PAIRING_KEY_INDEX, b"\x01" * 31)
