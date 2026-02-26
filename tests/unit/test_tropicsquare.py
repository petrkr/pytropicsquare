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
    CMD_ID_I_CFG_WRITE,
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
    MAC_AND_DESTROY_MAX,
    PAIRING_KEY_MAX)
from tropicsquare.constants.ecc import ECC_MAX_KEYS, ECC_CURVE_P256
from tropicsquare.constants.config import CFG_START_UP, CFG_UAP_PING
from tropicsquare.constants.l2 import (
    SLEEP_MODE_SLEEP,
    SLEEP_MODE_DEEP_SLEEP,
    STARTUP_REBOOT,
    STARTUP_MAINTENANCE_REBOOT,
)
from tropicsquare.config.startup import StartUpConfig
from tropicsquare.config.uap_operations import PingConfig
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


class TestPowerModeWrappers:
    """Test reboot() and sleep() wrappers."""

    @pytest.mark.parametrize("mode", [STARTUP_REBOOT, STARTUP_MAINTENANCE_REBOOT])
    def test_reboot_calls_l2_startup_req(self, mode):
        """Test reboot forwards mode to _l2.startup_req."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        seen = {}

        def mock_startup_req(mode):
            seen["mode"] = mode
            return True

        ts._l2.startup_req = mock_startup_req

        result = ts.reboot(mode)

        assert result is True
        assert seen["mode"] == mode

    def test_reboot_invalid_mode_raises_error(self):
        """Test reboot validates allowed startup modes."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        with pytest.raises(ValueError) as exc_info:
            ts.reboot(0xFF)

        assert "Invalid startup mode" in str(exc_info.value)

    @pytest.mark.parametrize("mode", [SLEEP_MODE_SLEEP, SLEEP_MODE_DEEP_SLEEP])
    def test_sleep_calls_l2_sleep_req(self, mode):
        """Test sleep forwards mode to _l2.sleep_req."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        seen = {}

        def mock_sleep_req(mode):
            seen["mode"] = mode
            return True

        ts._l2.sleep_req = mock_sleep_req

        result = ts.sleep(mode)

        assert result is True
        assert seen["mode"] == mode

    def test_sleep_invalid_mode_raises_error(self):
        """Test sleep validates allowed sleep modes."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        with pytest.raises(ValueError) as exc_info:
            ts.sleep(0xFF)

        assert "Invalid sleep mode" in str(exc_info.value)


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

        result = ts.ecc_key_read(0)

        assert result.curve == curve
        assert result.origin == origin
        assert result.public_key == pubkey

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

    def test_r_config_read_command(self, ts_with_session):
        """Test r_config_read command execution and auto-parsing."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 3-byte header + config data (4 bytes)
        config_data = b'\x12\x34\x56\x78'
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + config_data

        result = ts.r_config_read(CFG_START_UP)

        # Verify result is parsed config object
        assert isinstance(result, StartUpConfig)
        # Verify the underlying value is correct (config uses little-endian)
        assert result._value == int.from_bytes(config_data, 'little')

    def test_i_config_read_command(self, ts_with_session):
        """Test i_config_read command execution and auto-parsing."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 3-byte header + config data (4 bytes)
        config_data = b'\x12\x34\x56\x78'
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + config_data

        result = ts.i_config_read(CFG_START_UP)

        # Verify result is parsed config object
        assert isinstance(result, StartUpConfig)
        # Verify the underlying value is correct (config uses little-endian)
        assert result._value == int.from_bytes(config_data, 'little')

    def test_i_config_write_ping_uap_slot0_denied_payload(self, ts_with_session):
        """Test i_config_write payload for CFG_UAP_PING with slot 0 denied."""
        ts = ts_with_session

        captured = {}

        def capture_encrypted_command(size, ciphertext, tag):
            captured["size"] = size
            captured["ciphertext"] = ciphertext
            captured["tag"] = tag
            return (bytes([CMD_RESULT_OK]), b'\x00' * 16)

        ts._l2.encrypted_command = capture_encrypted_command

        ping_cfg = PingConfig()
        permissions = ping_cfg.permissions
        permissions.pkey_slot_0 = False
        ping_cfg.permissions = permissions

        result = ts.i_config_write(CFG_UAP_PING, ping_cfg)

        assert result is True
        assert captured["size"] == len(captured["ciphertext"])

        expected_payload = bytearray()
        expected_payload.append(CMD_ID_I_CFG_WRITE)
        expected_payload.extend(CFG_UAP_PING.to_bytes(2, "little"))
        expected_payload.extend(b"M")
        expected_payload.extend(ping_cfg.to_bytes())

        # MockAESGCM returns plaintext as ciphertext in unit tests, so we can
        # validate exact command bytes sent to L2 encrypted_command().
        assert captured["ciphertext"] == bytes(expected_payload)

    def test_ecc_key_store_command(self, ts_with_session):
        """Test ecc_key_store command execution."""
        ts = ts_with_session

        # Mock successful response
        ts.response_data = bytes([CMD_RESULT_OK])

        # P256 key (32 bytes)
        key = b'\x01' * 32
        result = ts.ecc_key_store(0, ECC_CURVE_P256, key)

        assert result == True

    def test_ecc_key_store_validates_slot(self, ts_with_session):
        """Test that ecc_key_store validates slot."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.ecc_key_store(ECC_MAX_KEYS + 1, ECC_CURVE_P256, b'\x01' * 32)

        assert "Slot is larger than ECC_MAX_KEYS" in str(exc_info.value)

    def test_ecc_key_store_validates_curve(self, ts_with_session):
        """Test that ecc_key_store validates curve."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.ecc_key_store(0, 0xFF, b'\x01' * 32)  # Invalid curve

        assert "Invalid curve" in str(exc_info.value)

    def test_ecdsa_sign_command(self, ts_with_session):
        """Test ecdsa_sign command execution."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 15 bytes padding + R (32) + S (32)
        # Note: _call_command strips first byte (CMD_RESULT_OK), leaving 15 + 32 + 32
        sign_r = b'\xAA' * 32
        sign_s = b'\xBB' * 32
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00' * 15 + sign_r + sign_s

        hash_value = b'\x01' * 32
        sign = ts.ecdsa_sign(0, hash_value)

        assert sign_r == sign.r
        assert sign_s == sign.s

    def test_ecdsa_sign_validates_slot(self, ts_with_session):
        """Test that ecdsa_sign validates slot."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.ecdsa_sign(ECC_MAX_KEYS + 1, b'\x01' * 32)

        assert "Slot is larger than ECC_MAX_KEYS" in str(exc_info.value)

    def test_eddsa_sign_command(self, ts_with_session):
        """Test eddsa_sign command execution."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 15 bytes padding + R (32) + S (32)
        # Note: _call_command strips first byte (CMD_RESULT_OK), leaving 15 + 32 + 32
        sign_r = b'\xCC' * 32
        sign_s = b'\xDD' * 32
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00' * 15 + sign_r + sign_s

        message = b'test message'
        sign = ts.eddsa_sign(0, message)

        assert sign_r == sign.r
        assert sign_s == sign.s

    def test_eddsa_sign_validates_slot(self, ts_with_session):
        """Test that eddsa_sign validates slot."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.eddsa_sign(ECC_MAX_KEYS + 1, b'message')

        assert "Slot is larger than ECC_MAX_KEYS" in str(exc_info.value)

    def test_mcounter_update_command(self, ts_with_session):
        """Test mcounter_update command execution."""
        ts = ts_with_session

        # Mock successful response
        ts.response_data = bytes([CMD_RESULT_OK])

        result = ts.mcounter_update(0)

        assert result == True

    def test_mcounter_update_validates_index(self, ts_with_session):
        """Test that mcounter_update validates index."""
        ts = ts_with_session

        with pytest.raises(ValueError) as exc_info:
            ts.mcounter_update(MCOUNTER_MAX + 1)

        assert "Index is larger than MCOUNTER_MAX" in str(exc_info.value)

    def test_mac_and_destroy_command(self, ts_with_session):
        """Test mac_and_destroy command execution."""
        ts = ts_with_session

        # Mock response: CMD_RESULT_OK + 3-byte header + MAC result (32 bytes)
        mac_result = b'\xEE' * 32
        ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + mac_result

        # Data must be exactly 32 bytes per API spec
        data = b'X' * 32
        result = ts.mac_and_destroy(0, data)

        # Verify 3-byte header is stripped
        assert result == mac_result

    def test_mac_and_destroy_validates_slot(self, ts_with_session):
        """Test that mac_and_destroy validates slot."""
        ts = ts_with_session

        # Valid 32-byte data for testing slot validation
        valid_data = b'X' * 32

        with pytest.raises(ValueError, match=r"exceeds maximum MAC_AND_DESTROY_MAX"):
            ts.mac_and_destroy(MAC_AND_DESTROY_MAX + 1, valid_data)

    def test_mac_and_destroy_validates_data_length(self, ts_with_session):
        """Test that MAC_And_Destroy validates data length (must be 32 bytes)."""
        ts = ts_with_session

        # Test too short data
        with pytest.raises(ValueError, match=r"Data must be exactly 32 bytes"):
            ts.mac_and_destroy(0, b'short')

        # Test too long data
        with pytest.raises(ValueError, match=r"Data must be exactly 32 bytes"):
            ts.mac_and_destroy(0, b'X' * 64)

        # Test correct length should not raise ValueError for data length
        # (will still fail with mock but validates length first)
        try:
            mac_result = b'\xEE' * 32
            ts.response_data = bytes([CMD_RESULT_OK]) + b'\x00\x00\x00' + mac_result
            ts.mac_and_destroy(0, b'X' * 32)  # Should not raise ValueError for data length
        except ValueError as e:
            if "Data must be exactly" in str(e):
                pytest.fail("Should not raise ValueError for 32-byte data")

    @pytest.mark.parametrize("slot", [-1, PAIRING_KEY_MAX + 1])
    def test_pairing_key_read_validates_slot_range(self, ts_with_session, slot):
        """Test pairing_key_read validates slot in range 0..PAIRING_KEY_MAX."""
        ts = ts_with_session

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            ts.pairing_key_read(slot)

    @pytest.mark.parametrize("slot", [-1, PAIRING_KEY_MAX + 1])
    def test_pairing_key_write_validates_slot_range(self, ts_with_session, slot):
        """Test pairing_key_write validates slot in range 0..PAIRING_KEY_MAX."""
        ts = ts_with_session

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            ts.pairing_key_write(slot, b"\x01" * 32)

    @pytest.mark.parametrize("slot", [-1, PAIRING_KEY_MAX + 1])
    def test_pairing_key_invalidate_validates_slot_range(self, ts_with_session, slot):
        """Test pairing_key_invalidate validates slot in range 0..PAIRING_KEY_MAX."""
        ts = ts_with_session

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            ts.pairing_key_invalidate(slot)

    def test_pairing_key_write_returns_true(self, ts_with_session):
        """Test pairing_key_write returns True on successful command."""
        ts = ts_with_session
        ts.response_data = bytes([CMD_RESULT_OK])

        assert ts.pairing_key_write(0, b"\xAA" * 32) is True


class TestStartSecureSession:
    """Test start_secure_session() method."""

    @pytest.mark.parametrize("pkey_index", [-1, PAIRING_KEY_MAX + 1])
    def test_start_secure_session_validates_pairing_slot(self, pkey_index):
        """Test start_secure_session validates pkey_index range before handshake."""
        from tropicsquare.ports.cpython import TropicSquareCPython

        transport = MockL1Transport()
        ts = TropicSquareCPython(transport)

        with pytest.raises(ValueError, match=r"Pairing key slot must be in range"):
            ts.start_secure_session(pkey_index, b'\x03' * 32, b'\x04' * 32)

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
