"""L2 basic communication tests.

Tests for L2 protocol layer communication without secure session.
These tests verify fundamental chip information retrieval using
TCP transport connection to the TROPIC01 model server.

All tests in this file operate at L2 level - no secure session required.
"""

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestBasicCommunication:
    """Test basic chip communication via TCP transport."""

    def test_tcp_transport_connection(self, tcp_transport):
        """Test that TCP transport can connect to model server.

        :param tcp_transport: TcpTransport fixture
        """
        # If fixture creation succeeded, connection works
        assert tcp_transport is not None

    def test_get_chipid(self, tropic_square):
        """Test reading chip ID from model.

        :param tropic_square: TropicSquare instance fixture
        """
        chipid = tropic_square.chipid

        assert chipid is not None
        assert chipid.serial_number is not None
        # Check parsed fields
        assert chipid.package_type_name is not None
        assert chipid.fab_name is not None

    def test_get_certificate(self, tropic_square):
        """Test reading X.509 certificate from model.

        :param tropic_square: TropicSquare instance fixture
        """
        # Get certificate (L2 command, no session needed)
        cert = tropic_square.certificate

        assert cert is not None
        assert isinstance(cert, bytes)
        assert len(cert) > 0

    def test_get_public_key(self, tropic_square):
        """Test reading public key from model.

        :param tropic_square: TropicSquare instance fixture
        """
        # Get public key (L2 command, no session needed)
        pubkey = tropic_square.public_key

        assert pubkey is not None
        assert isinstance(pubkey, bytes)
        assert len(pubkey) == 32  # Ed25519 public key is 32 bytes
