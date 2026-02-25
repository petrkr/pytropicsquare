"""Integration tests for PING authorization and reboot propagation."""

import pytest

from tropicsquare.constants.config import CFG_UAP_PING
from tropicsquare.constants.l2 import STARTUP_REBOOT
from tropicsquare.constants.pairing_keys import (
    FACTORY_PAIRING_KEY_INDEX,
    FACTORY_PAIRING_PRIVATE_KEY_PROD0,
    FACTORY_PAIRING_PUBLIC_KEY_PROD0,
)
from tropicsquare.exceptions import TropicSquareNoSession, TropicSquareUnauthorizedError


pytestmark = pytest.mark.integration


class TestPingAuthorization:
    """Test PING authorization behavior for pairing slots."""

    def test_ping_uap_slot1_denied_after_reboot(self, tropic_square):
        """CFG_UAP_PING change for slot 1 applies after reboot only."""
        slot_0 = FACTORY_PAIRING_KEY_INDEX
        slot_1 = 1
        ping_data = b"ping-auth-check"

        def _abort_if_active() -> None:
            try:
                tropic_square.abort_secure_session()
            except TropicSquareNoSession:
                pass

        try:
            _abort_if_active()

            tropic_square.start_secure_session(
                slot_0,
                FACTORY_PAIRING_PRIVATE_KEY_PROD0,
                FACTORY_PAIRING_PUBLIC_KEY_PROD0,
            )

            # Workflow step 1: copy factory pubkey from slot 0 to slot 1.
            key0 = tropic_square.pairing_key_read(slot_0)
            assert key0 == FACTORY_PAIRING_PUBLIC_KEY_PROD0
            assert tropic_square.pairing_key_write(slot_1, key0) is True
            assert tropic_square.pairing_key_read(slot_1) == key0

            ping_cfg = tropic_square.r_config_read(CFG_UAP_PING)
            permissions = ping_cfg.permissions
            permissions.pkey_slot_1 = False
            ping_cfg.permissions = permissions
            assert tropic_square.r_config_write(CFG_UAP_PING, ping_cfg) is True

            assert tropic_square.abort_secure_session() is True

            # Before reboot, slot 1 should still be authorized for PING.
            tropic_square.start_secure_session(
                slot_1,
                FACTORY_PAIRING_PRIVATE_KEY_PROD0,
                FACTORY_PAIRING_PUBLIC_KEY_PROD0,
            )
            assert tropic_square.ping(ping_data) == ping_data

            # Reboot applies new R-CONFIG values.
            assert tropic_square.reboot(STARTUP_REBOOT) is True

            tropic_square.start_secure_session(
                slot_1,
                FACTORY_PAIRING_PRIVATE_KEY_PROD0,
                FACTORY_PAIRING_PUBLIC_KEY_PROD0,
            )
            with pytest.raises(TropicSquareUnauthorizedError):
                tropic_square.ping(ping_data)

            assert tropic_square.abort_secure_session() is True

            tropic_square.start_secure_session(
                slot_0,
                FACTORY_PAIRING_PRIVATE_KEY_PROD0,
                FACTORY_PAIRING_PUBLIC_KEY_PROD0,
            )
            assert tropic_square.ping(ping_data) == ping_data

        finally:
            _abort_if_active()
