"""Tests for L2 Protocol Layer.

This module tests:
- L2Protocol initialization
- Request building with CRC
- All L2 protocol commands (get_info, handshake, encrypted_command, etc.)
- Chunking logic for large commands
- Response parsing
- Input validation
"""

import pytest
from tropicsquare.l2_protocol import L2Protocol
from tropicsquare.transports import L1Transport
from tropicsquare.constants.l2 import (
    REQ_ID_GET_INFO_REQ,
    REQ_ID_HANDSHARE_REQ,
    REQ_ID_GET_LOG_REQ,
    REQ_ID_ENCRYPTED_CMD_REQ,
    REQ_ID_ENCRYPTED_SESSION_ABT,
    REQ_ID_SLEEP_REQ,
    REQ_ID_STARTUP_REQ,
    SLEEP_MODE_SLEEP,
    SLEEP_MODE_DEEP_SLEEP,
    STARTUP_REBOOT,
    STARTUP_MAINTENANCE_REBOOT,
    COMMAND_SIZE_LEN,
)
from tropicsquare.constants.get_info_req import GET_INFO_CHIPID, GET_INFO_DATA_CHUNK_0_127
from tropicsquare.constants.chip_status import CHIP_STATUS_READY
from tropicsquare.exceptions import TropicSquareResponseError
from tropicsquare.crc import CRC


class MockL1Transport(L1Transport):
    """Mock L1Transport for testing L2Protocol."""

    def __init__(self):
        """Initialize mock transport."""
        self.send_request_calls = []
        self.get_response_calls = 0
        self.next_responses = []
        self.response_index = 0

    def send_request(self, request_data):
        """Mock send_request."""
        self.send_request_calls.append(bytes(request_data))
        return CHIP_STATUS_READY

    def get_response(self):
        """Mock get_response."""
        self.get_response_calls += 1
        if self.response_index < len(self.next_responses):
            response = self.next_responses[self.response_index]
            self.response_index += 1
            return response
        return b''

    def _transfer(self, tx_data):
        """Not used in L2 tests."""
        pass

    def _read(self, length):
        """Not used in L2 tests."""
        pass


class TestL2ProtocolInitialization:
    """Test L2Protocol initialization."""

    def test_init_stores_transport(self):
        """Test that initialization stores transport instance."""
        transport = MockL1Transport()
        l2 = L2Protocol(transport)
        assert l2._transport is transport


class TestBuildRequest:
    """Test _build_request() private method."""

    def test_build_request_with_payload(self):
        """Test building request with payload includes CRC."""
        transport = MockL1Transport()
        l2 = L2Protocol(transport)

        req_id = b'\x01\x02'
        payload = b'\x03\x04\x05'

        request = l2._build_request(req_id, payload)

        # Should be: req_id + payload + CRC(req_id + payload)
        expected_data = req_id + payload
        expected_crc = CRC.crc16(expected_data)

        assert request == expected_data + expected_crc
        assert len(request) == len(req_id) + len(payload) + 2

    def test_build_request_without_payload(self):
        """Test building request without payload."""
        transport = MockL1Transport()
        l2 = L2Protocol(transport)

        req_id = b'\x01\x02'

        request = l2._build_request(req_id)

        expected_crc = CRC.crc16(req_id)
        assert request == req_id + expected_crc

    def test_build_request_empty_payload(self):
        """Test building request with explicit empty payload."""
        transport = MockL1Transport()
        l2 = L2Protocol(transport)

        req_id = b'\x01\x02'
        request = l2._build_request(req_id, b'')

        expected_crc = CRC.crc16(req_id)
        assert request == req_id + expected_crc


class TestSendAndGetResponse:
    """Test _send_and_get_response() helper method."""

    def test_send_and_get_response_flow(self):
        """Test complete send and get response flow."""
        transport = MockL1Transport()
        transport.next_responses = [b'\x12\x34\x56']
        l2 = L2Protocol(transport)

        req_id = b'\x01\x02'
        payload = b'\x03\x04'

        result = l2._send_and_get_response(req_id, payload)

        # Check that request was sent
        assert len(transport.send_request_calls) == 1

        # Check that request has CRC
        sent_request = transport.send_request_calls[0]
        expected_data = req_id + payload
        expected_crc = CRC.crc16(expected_data)
        assert sent_request == expected_data + expected_crc

        # Check response
        assert result == b'\x12\x34\x56'
        assert transport.get_response_calls == 1


class TestGetInfoReq:
    """Test get_info_req() method."""

    def test_get_info_req_chip_id(self):
        """Test getting chip ID."""
        transport = MockL1Transport()
        chip_id_data = b'\x01' * 128
        transport.next_responses = [chip_id_data]
        l2 = L2Protocol(transport)

        result = l2.get_info_req(GET_INFO_CHIPID)

        assert result == chip_id_data
        assert len(transport.send_request_calls) == 1

        # Verify payload format
        sent_request = transport.send_request_calls[0]
        # Should contain REQ_ID_GET_INFO_REQ + [object_id, chunk] + CRC
        assert GET_INFO_CHIPID in sent_request
        assert GET_INFO_DATA_CHUNK_0_127 in sent_request

    def test_get_info_req_with_custom_chunk(self):
        """Test get_info with custom data chunk."""
        transport = MockL1Transport()
        transport.next_responses = [b'\x00' * 128]
        l2 = L2Protocol(transport)

        custom_chunk = 0x02
        l2.get_info_req(GET_INFO_CHIPID, custom_chunk)

        sent_request = transport.send_request_calls[0]
        assert custom_chunk.to_bytes(1, 'big') in sent_request


class TestHandshakeReq:
    """Test handshake_req() method."""

    def test_handshake_req_parses_response(self):
        """Test that handshake parses tsehpub and tsauth correctly."""
        transport = MockL1Transport()
        tsehpub = b'\x01' * 32
        tsauth = b'\x02' * 16
        transport.next_responses = [tsehpub + tsauth]
        l2 = L2Protocol(transport)

        ehpub = b'\x03' * 32
        p_keyslot = 0

        result_ehpub, result_auth = l2.handshake_req(ehpub, p_keyslot)

        assert result_ehpub == tsehpub
        assert result_auth == tsauth
        assert len(transport.send_request_calls) == 1

    def test_handshake_req_payload_format(self):
        """Test that handshake request has correct payload."""
        transport = MockL1Transport()
        transport.next_responses = [b'\x00' * 48]
        l2 = L2Protocol(transport)

        ehpub = b'\xAB' * 32
        p_keyslot = 2

        l2.handshake_req(ehpub, p_keyslot)

        sent_request = transport.send_request_calls[0]
        # Payload should be ehpub (32 bytes) + p_keyslot (1 byte)
        assert ehpub in sent_request
        assert p_keyslot.to_bytes(1, 'big') in sent_request


class TestGetLog:
    """Test get_log() method."""

    def test_get_log(self):
        """Test getting firmware logs."""
        transport = MockL1Transport()
        log_data = b'Log message from firmware'
        transport.next_responses = [log_data]
        l2 = L2Protocol(transport)

        result = l2.get_log()

        assert result == log_data
        assert len(transport.send_request_calls) == 1


class TestEncryptedCommand:
    """Test encrypted_command() method."""

    def test_encrypted_command_single_chunk(self):
        """Test encrypted command that fits in single chunk."""
        transport = MockL1Transport()

        # Response: size (2 bytes) + ciphertext + tag (16 bytes)
        response_ciphertext = b'\x12\x34'
        response_tag = b'\x56' * 16
        response_size = len(response_ciphertext).to_bytes(2, 'little')
        response_data = response_size + response_ciphertext + response_tag

        # Two responses: ACK for chunk, final response
        transport.next_responses = [b'', response_data]
        l2 = L2Protocol(transport)

        command_ciphertext = b'\xAB\xCD'
        command_tag = b'\xEF' * 16
        command_size = len(command_ciphertext)

        result_ciphertext, result_tag = l2.encrypted_command(
            command_size, command_ciphertext, command_tag
        )

        assert result_ciphertext == response_ciphertext
        assert result_tag == response_tag
        assert transport.get_response_calls == 2  # ACK + final response

    def test_encrypted_command_multiple_chunks(self):
        """Test encrypted command with multiple chunks (> 128 bytes)."""
        transport = MockL1Transport()

        # Large command requiring chunking
        command_ciphertext = b'\xAB' * 200
        command_tag = b'\xCD' * 16
        command_size = len(command_ciphertext)

        # Calculate expected number of chunks
        l3data_size = 2 + len(command_ciphertext) + 16  # size + ciphertext + tag
        num_chunks = (l3data_size + 127) // 128  # Ceil division

        # ACK responses for each chunk + final response
        response_ciphertext = b'\x12\x34'
        response_tag = b'\x56' * 16
        response_size = len(response_ciphertext).to_bytes(2, 'little')
        response_data = response_size + response_ciphertext + response_tag

        transport.next_responses = [b''] * num_chunks + [response_data]
        l2 = L2Protocol(transport)

        result_ciphertext, result_tag = l2.encrypted_command(
            command_size, command_ciphertext, command_tag
        )

        assert result_ciphertext == response_ciphertext
        assert result_tag == response_tag
        assert len(transport.send_request_calls) == num_chunks

    def test_encrypted_command_size_mismatch_raises_error(self):
        """Test that size mismatch in response raises error."""
        transport = MockL1Transport()

        # Response claims 10 bytes but only has 2
        wrong_size = (10).to_bytes(2, 'little')
        actual_ciphertext = b'\x12\x34'
        response_tag = b'\x56' * 16
        response_data = wrong_size + actual_ciphertext + response_tag

        transport.next_responses = [b'', response_data]
        l2 = L2Protocol(transport)

        with pytest.raises(TropicSquareResponseError) as exc_info:
            l2.encrypted_command(2, b'\xAB\xCD', b'\xEF' * 16)

        assert "Command size mismatch" in str(exc_info.value)


class TestEncryptedSessionAbt:
    """Test encrypted_session_abt() method."""

    def test_encrypted_session_abt(self):
        """Test aborting encrypted session."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.encrypted_session_abt()

        assert result is True
        assert len(transport.send_request_calls) == 1


class TestSleepReq:
    """Test sleep_req() method."""

    def test_sleep_req_normal_sleep(self):
        """Test normal sleep mode."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.sleep_req(SLEEP_MODE_SLEEP)

        assert result is True
        assert len(transport.send_request_calls) == 1

        # Check payload contains sleep mode
        sent_request = transport.send_request_calls[0]
        assert SLEEP_MODE_SLEEP.to_bytes(1, 'big') in sent_request

    def test_sleep_req_deep_sleep(self):
        """Test deep sleep mode."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.sleep_req(SLEEP_MODE_DEEP_SLEEP)

        assert result is True

    def test_sleep_req_accepts_raw_mode_value(self):
        """Test that sleep_req forwards mode value without local validation."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.sleep_req(0xFF)

        assert result is True
        sent_request = transport.send_request_calls[0]
        assert b'\xFF' in sent_request


class TestStartupReq:
    """Test startup_req() method."""

    def test_startup_req_normal_reboot(self):
        """Test normal reboot."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.startup_req(STARTUP_REBOOT)

        assert result is True
        assert len(transport.send_request_calls) == 1

    def test_startup_req_maintenance_reboot(self):
        """Test maintenance reboot."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.startup_req(STARTUP_MAINTENANCE_REBOOT)

        assert result is True

    def test_startup_req_accepts_raw_mode_value(self):
        """Test that startup_req forwards mode value without local validation."""
        transport = MockL1Transport()
        transport.next_responses = [b'']
        l2 = L2Protocol(transport)

        result = l2.startup_req(0xFF)

        assert result is True
        sent_request = transport.send_request_calls[0]
        assert b'\xFF' in sent_request
