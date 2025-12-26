"""Tests for TropicSquare main class.

This module tests:
- TropicSquare initialization and factory method
- Properties (certificate, public_key, chipid, firmware versions)
- get_log() method
- _call_command() encrypt/decrypt flow
- L3 command execution
- Secure session management
- Error handling and validation
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from tropicsquare import TropicSquare
from tropicsquare.l2_protocol import L2Protocol
from tropicsquare.chip_id import ChipId
from tropicsquare.exceptions import (
    TropicSquareError,
    TropicSquareNoSession,
    TropicSquareHandshakeError,
)
from tropicsquare.constants.cmd_result import CMD_RESULT_OK, CMD_RESULT_FAIL
from tropicsquare.constants.get_info_req import (
    GET_INFO_X509_CERT,
    GET_INFO_CHIPID,
    GET_INFO_RISCV_FW_VERSION,
    GET_INFO_SPECT_FW_VERSION,
    GET_INFO_FW_BANK,
    GET_INFO_DATA_CHUNK_0_127,
    GET_INFO_DATA_CHUNK_128_255,
    GET_INFO_DATA_CHUNK_256_383,
    GET_INFO_DATA_CHUNK_384_511,
)
from tropicsquare.constants import (
    CMD_ID_PING,
    CMD_ID_RANDOM_VALUE,
    CMD_ID_R_MEMDATA_WRITE,
    CMD_ID_R_MEMDATA_READ,
    CMD_ID_R_MEMDATA_ERASE,
    CMD_ID_ECC_KEY_GENERATE,
    CMD_ID_ECC_KEY_READ,
    CMD_ID_ECC_KEY_ERASE,
    CMD_ID_MCOUNTER_INIT,
    CMD_ID_MCOUNTER_GET,
    MEM_DATA_MAX_SIZE,
    MCOUNTER_MAX,
    MAC_AND_DESTROY_MAX)
from tropicsquare.constants.ecc import ECC_MAX_KEYS, ECC_CURVE_P256
from tropicsquare.constants.config import CFG_START_UP
from tropicsquare.config.startup import StartUpConfig
from tests.conftest import MockL1Transport, MockAESGCM


class TestTropicSquareFactoryMethod:
    """Test TropicSquare factory method (__new__)."""

    def test_factory_returns_cpython_on_cpython(self):
        """Test that TropicSquare returns CPython implementation on CPython."""
        # We're running on CPython during tests
        assert sys.implementation.name == 'cpython'

        # Mock transport
        transport = MockL1Transport()

        # Instantiate should return CPython implementation
        ts = TropicSquare.__new__(TropicSquare, transport)

        # Should import and return TropicSquareCPython
        from tropicsquare.ports.cpython import TropicSquareCPython
        assert isinstance(ts, TropicSquareCPython)

    @pytest.mark.skip(reason="Complex sys.implementation mocking - tested in integration")
    @patch('sys.implementation')
    def test_factory_returns_micropython_on_micropython(self, mock_impl):
        """Test that TropicSquare returns MicroPython implementation on MicroPython."""
        # Mock sys.implementation to be micropython
        mock_impl.name = 'micropython'

        transport = MockL1Transport()

        # Should return MicroPython implementation
        ts = TropicSquare.__new__(TropicSquare, transport)

        from tropicsquare.ports.micropython import TropicSquareMicroPython
        assert isinstance(ts, TropicSquareMicroPython)

    @patch('sys.implementation')
    def test_factory_raises_error_on_unsupported_platform(self, mock_impl):
        """Test that unsupported Python implementation raises error."""
        # Mock unsupported implementation
        mock_impl.name = 'pypy'

        transport = MockL1Transport()

        with pytest.raises(TropicSquareError) as exc_info:
            TropicSquare.__new__(TropicSquare, transport)

        assert "Unsupported Python implementation" in str(exc_info.value)
        assert "pypy" in str(exc_info.value)

    def test_subclass_instantiation_bypasses_factory(self):
        """Test that subclass instantiation bypasses factory logic."""
        # When instantiating a subclass directly, __new__ should not do factory logic
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()

        # Direct instantiation should work
        ts = TropicSquareCPython(transport)
        assert isinstance(ts, TropicSquareCPython)


class TestTropicSquareInitialization:
    """Test TropicSquare initialization."""

    def test_init_creates_l2_protocol(self):
        """Test that __init__ creates L2Protocol instance."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        assert ts._l2 is not None
        assert isinstance(ts._l2, L2Protocol)

    def test_init_sets_session_to_none(self):
        """Test that __init__ sets _secure_session to None."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        assert ts._secure_session is None

    def test_init_sets_certificate_to_none(self):
        """Test that __init__ sets _certificate to None."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        assert ts._certificate is None


class TestTropicSquareProperties:
    """Test TropicSquare property methods."""

    def test_certificate_property_fetches_in_chunks(self):
        """Test that certificate property fetches cert in 4 chunks."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        # Create certificate data:
        # 10 bytes header + certificate
        cert_data = b'CERT' * 100  # 400 bytes certificate
        header = b'\x00\x00' + len(cert_data).to_bytes(2, 'big') + b'\x00' * 6
        full_data = header + cert_data

        # Split into 4 chunks of 128 bytes each
        chunk1 = full_data[0:128]
        chunk2 = full_data[128:256]
        chunk3 = full_data[256:384]
        chunk4 = full_data[384:512]

        transport = MockL1Transport(responses=[chunk1, chunk2, chunk3, chunk4])
        ts = TropicSquareCPython(transport)

        # Mock L2 get_info_req to return chunks
        call_count = [0]
        def mock_get_info(obj_id, chunk_id=GET_INFO_DATA_CHUNK_0_127):
            idx = call_count[0]
            call_count[0] += 1
            return [chunk1, chunk2, chunk3, chunk4][idx]

        ts._l2.get_info_req = mock_get_info

        # Get certificate
        cert = ts.certificate

        # Should extract certificate from data (skip 10 byte header)
        assert cert == cert_data
        assert call_count[0] == 4

    def test_certificate_property_caches_result(self):
        """Test that certificate property caches result."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        cert_data = b'CERT' * 100
        header = b'\x00\x00' + len(cert_data).to_bytes(2, 'big') + b'\x00' * 6
        full_data = header + cert_data

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        call_count = [0]
        def mock_get_info(obj_id, chunk_id=GET_INFO_DATA_CHUNK_0_127):
            call_count[0] += 1
            offset = (chunk_id) * 128
            return full_data[offset:offset+128]

        ts._l2.get_info_req = mock_get_info

        # First call
        cert1 = ts.certificate
        first_call_count = call_count[0]

        # Second call - should use cached value
        cert2 = ts.certificate

        assert cert1 == cert2
        assert call_count[0] == first_call_count  # No additional calls

    def test_public_key_property_extracts_from_certificate(self):
        """Test that public_key extracts key from certificate."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        # Create certificate with signature pattern
        pubkey = b'\xAB' * 32
        cert = b'\x00' * 50 + b'\x65\x6e\x03\x21\x00' + pubkey + b'\x00' * 50

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)
        ts._certificate = cert

        # Get public key
        key = ts.public_key

        assert key == pubkey

    def test_public_key_loads_certificate_if_not_cached(self):
        """Test that public_key loads certificate if not already cached."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        pubkey = b'\xAB' * 32
        cert = b'\x00' * 50 + b'\x65\x6e\x03\x21\x00' + pubkey + b'\x00' * 50
        header = b'\x00\x00' + len(cert).to_bytes(2, 'big') + b'\x00' * 6
        full_data = header + cert

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        def mock_get_info(obj_id, chunk_id=GET_INFO_DATA_CHUNK_0_127):
            offset = chunk_id * 128
            return full_data[offset:offset+128]

        ts._l2.get_info_req = mock_get_info

        # Certificate not loaded yet
        assert ts._certificate is None

        # Get public key - should trigger certificate load
        key = ts.public_key

        assert key == pubkey
        assert ts._certificate is not None

    def test_public_key_returns_none_if_signature_not_found(self):
        """Test that public_key returns None if signature not found."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        # Certificate without signature pattern
        cert = b'\x00' * 200

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)
        ts._certificate = cert

        key = ts.public_key

        assert key is None

    def test_chipid_property_returns_parsed_chip_id(self):
        """Test that chipid property returns parsed ChipId object."""
        from tropicsquare.ports.cpython import TropicSquareCPython
        from tests.fixtures.chip_id_responses import CHIP_ID_SAMPLE

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Use real chip ID data from hardware fixture
        ts._l2.get_info_req = lambda obj_id: CHIP_ID_SAMPLE

        chip_id = ts.chipid

        assert isinstance(chip_id, ChipId)
        # Verify it parsed the real data correctly
        assert chip_id.serial_number is not None

    def test_riscv_fw_version_property(self):
        """Test RISCV firmware version property."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        # Version data: release, patch, minor, major (reversed in response)
        version_data = b'\x04\x03\x02\x01' + b'\x00' * 124

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        ts._l2.get_info_req = lambda obj_id: version_data

        version = ts.riscv_fw_version

        # Should return (major, minor, patch, release)
        assert version == (1, 2, 3, 4)

    def test_spect_fw_version_property(self):
        """Test SPECT firmware version property."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        version_data = b'\x08\x07\x06\x05' + b'\x00' * 124

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        ts._l2.get_info_req = lambda obj_id: version_data

        version = ts.spect_fw_version

        assert version == (5, 6, 7, 8)

    def test_fw_bank_property(self):
        """Test firmware bank property."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        bank_data = b'\x01' + b'\x00' * 127

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        ts._l2.get_info_req = lambda obj_id: bank_data

        bank = ts.fw_bank

        assert bank == bank_data


class TestGetLog:
    """Test get_log() method."""

    def test_get_log_returns_decoded_string(self):
        """Test that get_log returns decoded UTF-8 string."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        log_parts = [b'Hello ', b'World', b'']

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        call_count = [0]
        def mock_get_log():
            if call_count[0] < len(log_parts):
                part = log_parts[call_count[0]]
                call_count[0] += 1
                return part
            return b''

        ts._l2.get_log = mock_get_log

        log = ts.get_log()

        assert log == 'Hello World'

    def test_get_log_handles_empty_log(self):
        """Test that get_log handles empty log."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        ts._l2.get_log = lambda: b''

        log = ts.get_log()

        assert log == ''


class TestAbstractMethods:
    """Test that abstract methods raise NotImplementedError."""

    def test_get_ephemeral_keypair_not_implemented(self):
        """Test _get_ephemeral_keypair raises NotImplementedError."""
        # Create minimal subclass that doesn't implement abstract methods
        class MinimalTropicSquare(TropicSquare):
            pass

        transport = MockL1Transport()
        ts = object.__new__(MinimalTropicSquare)
        TropicSquare.__init__(ts, transport)

        with pytest.raises(NotImplementedError):
            ts._get_ephemeral_keypair()

    def test_hkdf_not_implemented(self):
        """Test _hkdf raises NotImplementedError."""
        class MinimalTropicSquare(TropicSquare):
            pass

        transport = MockL1Transport()
        ts = object.__new__(MinimalTropicSquare)
        TropicSquare.__init__(ts, transport)

        with pytest.raises(NotImplementedError):
            ts._hkdf(b'salt', b'secret', 1)

    def test_x25519_exchange_not_implemented(self):
        """Test _x25519_exchange raises NotImplementedError."""
        class MinimalTropicSquare(TropicSquare):
            pass

        transport = MockL1Transport()
        ts = object.__new__(MinimalTropicSquare)
        TropicSquare.__init__(ts, transport)

        with pytest.raises(NotImplementedError):
            ts._x25519_exchange(b'\x00' * 32, b'\x00' * 32)

    def test_aesgcm_not_implemented(self):
        """Test _aesgcm raises NotImplementedError."""
        class MinimalTropicSquare(TropicSquare):
            pass

        transport = MockL1Transport()
        ts = object.__new__(MinimalTropicSquare)
        TropicSquare.__init__(ts, transport)

        with pytest.raises(NotImplementedError):
            ts._aesgcm(b'\x00' * 32)


class TestCallCommand:
    """Test _call_command() method."""

    def test_call_command_raises_error_without_session(self):
        """Test that _call_command raises TropicSquareNoSession without session."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # No session established
        assert ts._secure_session is None

        with pytest.raises(TropicSquareNoSession) as exc_info:
            ts._call_command(b'\x01\x02\x03')

        assert "Secure session not started" in str(exc_info.value)

    def test_call_command_encrypts_and_sends(self):
        """Test that _call_command encrypts data and sends via L2."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Set up mock session with MockAESGCM
        encrypt_key = MockAESGCM()
        decrypt_key = MockAESGCM()
        ts._secure_session = [encrypt_key, decrypt_key, 0]

        # Mock L2 encrypted_command to return response
        response_data = bytes([CMD_RESULT_OK]) + b'response_data'
        ts._l2.encrypted_command = lambda size, ciphertext, tag: (response_data, b'\x00' * 16)

        # Call command
        command_data = b'\x01\x02\x03'
        result = ts._call_command(command_data)

        # Should return decrypted response (without first byte which is result code)
        assert result == b'response_data'

    def test_call_command_increments_counter(self):
        """Test that _call_command increments session counter."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Set up mock session
        encrypt_key = MockAESGCM()
        decrypt_key = MockAESGCM()
        ts._secure_session = [encrypt_key, decrypt_key, 5]

        # Mock L2 encrypted_command
        response_data = bytes([CMD_RESULT_OK]) + b'data'
        ts._l2.encrypted_command = lambda size, ciphertext, tag: (response_data, b'\x00' * 16)

        # Counter should be 5
        assert ts._secure_session[2] == 5

        # Call command
        ts._call_command(b'\x01')

        # Counter should be incremented to 6
        assert ts._secure_session[2] == 6

    def test_call_command_raises_error_on_cmd_result_fail(self):
        """Test that _call_command raises error on CMD_RESULT_FAIL."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Set up mock session
        encrypt_key = MockAESGCM()
        decrypt_key = MockAESGCM()
        ts._secure_session = [encrypt_key, decrypt_key, 0]

        # Mock L2 to return FAIL result
        response_data = bytes([CMD_RESULT_FAIL]) + b'data'
        ts._l2.encrypted_command = lambda size, ciphertext, tag: (response_data, b'\x00' * 16)

        # Should raise error due to CMD_RESULT_FAIL
        with pytest.raises(TropicSquareError):
            ts._call_command(b'\x01')


class TestAbortSecureSession:
    """Test abort_secure_session() method."""

    def test_abort_secure_session_clears_session(self):
        """Test that abort_secure_session clears session."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Set up mock session
        ts._secure_session = [MockAESGCM(), MockAESGCM(), 0]

        # Mock L2 encrypted_session_abt
        ts._l2.encrypted_session_abt = lambda: True

        result = ts.abort_secure_session()

        assert result is True
        assert ts._secure_session is None

    def test_abort_secure_session_returns_false_on_failure(self):
        """Test that abort_secure_session returns False on failure."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        ts._secure_session = [MockAESGCM(), MockAESGCM(), 0]

        # Mock L2 to return False
        ts._l2.encrypted_session_abt = lambda: False

        result = ts.abort_secure_session()

        assert result is False
        # Session should still be set
        assert ts._secure_session is not None


class TestL3Commands:
    """Test L3 command methods."""

    @pytest.fixture
    def ts_with_session(self):
        """Provide TropicSquare instance with mock session."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Set up mock session
        encrypt_key = MockAESGCM()
        decrypt_key = MockAESGCM()
        ts._secure_session = [encrypt_key, decrypt_key, 0]

        # Mock L2 encrypted_command
        ts.response_data = None
        def mock_encrypted_command(size, ciphertext, tag):
            # Return mock response (ciphertext, tag)
            # decrypt() will concatenate them and remove last 16 bytes
            if ts.response_data:
                return (ts.response_data, b'\x00' * 16)
            return (bytes([CMD_RESULT_OK]) + b'test', b'\x00' * 16)

        ts._l2.encrypted_command = mock_encrypted_command

        return ts

    def test_ping_command(self, ts_with_session):
        """Test ping command."""
        ts = ts_with_session

        # Mock response
        ping_data = b'hello'
        ts.response_data = bytes([CMD_RESULT_OK]) + ping_data

        result = ts.ping(ping_data)

        assert result == ping_data

    def test_get_random_command(self, ts_with_session):
        """Test get_random command."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 3 bytes header + random data
        random_data = b'\xAB\xCD\xEF\x01\x02'
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + random_data

        result = ts.get_random(5)

        # Should strip first 3 bytes after CMD_RESULT
        assert result == random_data

    def test_mem_data_write_command(self, ts_with_session):
        """Test mem_data_write command."""
        ts = ts_with_session

        data = b'test data'
        slot = 0

        ts.response_data = bytes([CMD_RESULT_OK])

        result = ts.mem_data_write(data, slot)

        assert result is True

    def test_mem_data_write_validates_size(self, ts_with_session):
        """Test that mem_data_write validates data size."""
        ts = ts_with_session

        # Data larger than MEM_DATA_MAX_SIZE
        large_data = b'X' * (MEM_DATA_MAX_SIZE + 1)

        with pytest.raises(ValueError) as exc_info:
            ts.mem_data_write(large_data, 0)

        assert "exceeds maximum allowed size" in str(exc_info.value)

    def test_mem_data_read_command(self, ts_with_session):
        """Test mem_data_read command."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 3 bytes + data
        mem_data = b'stored data'
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + mem_data

        result = ts.mem_data_read(0)

        assert result == mem_data

    def test_mem_data_erase_command(self, ts_with_session):
        """Test mem_data_erase command."""
        ts = ts_with_session

        ts.response_data = bytes([CMD_RESULT_OK])

        result = ts.mem_data_erase(0)

        assert result is True

    def test_ecc_key_generate_command(self, ts_with_session):
        """Test ecc_key_generate command."""
        ts = ts_with_session

        ts.response_data = bytes([CMD_RESULT_OK])

        result = ts.ecc_key_generate(0, ECC_CURVE_P256)

        assert result is True

    def test_ecc_key_generate_validates_slot(self, ts_with_session):
        """Test that ecc_key_generate validates slot."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.ecc_key_generate(ECC_MAX_KEYS + 1, ECC_CURVE_P256)

        assert "Slot is larger than ECC_MAX_KEYS" in str(exc_info.value)

    def test_ecc_key_generate_validates_curve(self, ts_with_session):
        """Test that ecc_key_generate validates curve."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.ecc_key_generate(0, 0xFF)

        assert "Invalid curve" in str(exc_info.value)

    def test_ecc_key_read_command(self, ts_with_session):
        """Test ecc_key_read command."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + curve + origin + 13 bytes padding + pubkey
        # pubkey = result[15:], so need curve(0) + origin(1) + padding(2-14) + pubkey(15+)
        curve = ECC_CURVE_P256
        origin = 0x01
        pubkey = b'\xAB' * 32
        ts.response_data = bytes([CMD_RESULT_OK, curve, origin]) + b'\x00' * 13 + pubkey

        result_curve, result_origin, result_pubkey = ts.ecc_key_read(0)

        assert result_curve == curve
        assert result_origin == origin
        assert result_pubkey == pubkey

    def test_ecc_key_erase_command(self, ts_with_session):
        """Test ecc_key_erase command."""
        ts = ts_with_session

        ts.response_data = bytes([CMD_RESULT_OK])

        result = ts.ecc_key_erase(0)

        assert result is True

    def test_mcounter_init_command(self, ts_with_session):
        """Test mcounter_init command."""
        ts = ts_with_session

        ts.response_data = bytes([CMD_RESULT_OK])

        result = ts.mcounter_init(0, 100)

        assert result is True

    def test_mcounter_init_validates_index(self, ts_with_session):
        """Test that mcounter_init validates index."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.mcounter_init(MCOUNTER_MAX + 1, 100)

        assert "Index is larger than MCOUNTER_MAX" in str(exc_info.value)

    def test_mcounter_get_command(self, ts_with_session):
        """Test mcounter_get command."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 3 bytes + counter value (little-endian)
        counter_value = 42
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + counter_value.to_bytes(4, 'little')

        result = ts.mcounter_get(0)

        assert result == counter_value


class TestStartSecureSession:
    """Test start_secure_session() method."""

    def test_start_secure_session_auth_tag_mismatch_raises_error(self):
        """Test that auth tag mismatch raises TropicSquareHandshakeError."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        # Mock certificate and public key
        pubkey = b'\x01' * 32
        cert = b'\x00' * 50 + b'\x65\x6e\x03\x21\x00' + pubkey + b'\x00' * 50
        ts._certificate = cert

        # Mock L2 handshake to return mismatched auth tag
        tsehpub = b'\x02' * 32
        tsauth = b'\xFF' * 16  # Wrong auth tag
        ts._l2.handshake_req = lambda ehpub, pkey_idx: (tsehpub, tsauth)

        # Try to start session - should fail on auth tag mismatch
        with pytest.raises(TropicSquareHandshakeError) as exc_info:
            ts.start_secure_session(0, b'\x03' * 32, b'\x04' * 32)

        assert "Authentication tag mismatch" in str(exc_info.value)
