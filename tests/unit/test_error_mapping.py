"""Tests for error code to exception mapping.

This module tests:
- CMD_RESULT code to exception mapping
- RSP_STATUS code to exception mapping
- Exception raising functions
- Unknown error code handling
"""

import pytest
from tropicsquare.error_mapping import (
    map_cmd_result_to_exception,
    map_response_status_to_exception,
    raise_for_cmd_result,
    raise_for_response_status,
)
from tropicsquare.exceptions import (
    TropicSquareError,
    TropicSquareCRCError,
    TropicSquareNoSession,
    TropicSquareTimeoutError,
    TropicSquareCommandError,
    TropicSquareUnauthorizedError,
    TropicSquareInvalidCommandError,
    TropicSquareMemoryWriteError,
    TropicSquareMemorySlotExpiredError,
    TropicSquareECCInvalidKeyError,
    TropicSquareCounterUpdateError,
    TropicSquareCounterInvalidError,
    TropicSquareHandshakeError,
    TropicSquareTagError,
    TropicSquareResponseError,
)
from tropicsquare.constants.cmd_result import (
    CMD_RESULT_OK,
    CMD_RESULT_FAIL,
    CMD_RESULT_UNAUTHORIZED,
    CMD_RESULT_INVALID_CMD,
    CMD_RESULT_MEM_WRITE_FAIL,
    CMD_RESULT_MEM_SLOT_EXPIRED,
    CMD_RESULT_ECC_INVALID_KEY,
    CMD_RESULT_MCOUNTER_UPDATE_ERROR,
    CMD_RESULT_MCOUNTER_COUNTER_INVALID,
)
from tropicsquare.constants.rsp_status import (
    RSP_STATUS_REQ_OK,
    RSP_STATUS_RES_OK,
    RSP_STATUS_REQ_CONT,
    RSP_STATUS_RES_CONT,
    RSP_STATUS_RESP_DISABLED,
    RSP_STATUS_HSK_ERROR,
    RSP_STATUS_NO_SESSION,
    RSP_STATUS_TAG_ERROR,
    RSP_STATUS_CRC_ERROR,
    RSP_STATUS_UNKNOWN_REQ,
    RSP_STATUS_GEN_ERROR,
    RSP_STATUS_NO_RESPONSE,
)


class TestCmdResultMapping:
    """Test CMD_RESULT code to exception mapping."""

    def test_map_cmd_result_fail(self):
        """Test mapping CMD_RESULT_FAIL to TropicSquareCommandError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_FAIL)
        assert isinstance(exc, TropicSquareCommandError)
        assert "Command execution failed" in str(exc)
        assert hex(CMD_RESULT_FAIL) in str(exc)

    def test_map_cmd_result_unauthorized(self):
        """Test mapping CMD_RESULT_UNAUTHORIZED to TropicSquareUnauthorizedError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_UNAUTHORIZED)
        assert isinstance(exc, TropicSquareUnauthorizedError)
        assert "Command not authorized" in str(exc)
        assert hex(CMD_RESULT_UNAUTHORIZED) in str(exc)

    def test_map_cmd_result_invalid_cmd(self):
        """Test mapping CMD_RESULT_INVALID_CMD to TropicSquareInvalidCommandError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_INVALID_CMD)
        assert isinstance(exc, TropicSquareInvalidCommandError)
        assert "Invalid command" in str(exc)
        assert hex(CMD_RESULT_INVALID_CMD) in str(exc)

    def test_map_cmd_result_mem_write_fail(self):
        """Test mapping CMD_RESULT_MEM_WRITE_FAIL to TropicSquareMemoryWriteError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_MEM_WRITE_FAIL)
        assert isinstance(exc, TropicSquareMemoryWriteError)
        assert "Memory write operation failed" in str(exc)
        assert hex(CMD_RESULT_MEM_WRITE_FAIL) in str(exc)

    def test_map_cmd_result_mem_slot_expired(self):
        """Test mapping CMD_RESULT_MEM_SLOT_EXPIRED to TropicSquareMemorySlotExpiredError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_MEM_SLOT_EXPIRED)
        assert isinstance(exc, TropicSquareMemorySlotExpiredError)
        assert "Memory slot has expired" in str(exc)
        assert hex(CMD_RESULT_MEM_SLOT_EXPIRED) in str(exc)

    def test_map_cmd_result_ecc_invalid_key(self):
        """Test mapping CMD_RESULT_ECC_INVALID_KEY to TropicSquareECCInvalidKeyError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_ECC_INVALID_KEY)
        assert isinstance(exc, TropicSquareECCInvalidKeyError)
        assert "ECC key is invalid or not found" in str(exc)
        assert hex(CMD_RESULT_ECC_INVALID_KEY) in str(exc)

    def test_map_cmd_result_mcounter_update_error(self):
        """Test mapping CMD_RESULT_MCOUNTER_UPDATE_ERROR to TropicSquareCounterUpdateError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_MCOUNTER_UPDATE_ERROR)
        assert isinstance(exc, TropicSquareCounterUpdateError)
        assert "Monotonic counter update failed" in str(exc)
        assert hex(CMD_RESULT_MCOUNTER_UPDATE_ERROR) in str(exc)

    def test_map_cmd_result_mcounter_counter_invalid(self):
        """Test mapping CMD_RESULT_MCOUNTER_COUNTER_INVALID to TropicSquareCounterInvalidError."""
        exc = map_cmd_result_to_exception(CMD_RESULT_MCOUNTER_COUNTER_INVALID)
        assert isinstance(exc, TropicSquareCounterInvalidError)
        assert "Invalid monotonic counter" in str(exc)
        assert hex(CMD_RESULT_MCOUNTER_COUNTER_INVALID) in str(exc)

    def test_map_unknown_cmd_result(self):
        """Test mapping unknown CMD_RESULT to default TropicSquareCommandError."""
        unknown_code = 0xFF
        exc = map_cmd_result_to_exception(unknown_code)
        assert isinstance(exc, TropicSquareCommandError)
        assert "Command failed" in str(exc)
        assert hex(unknown_code) in str(exc)


class TestResponseStatusMapping:
    """Test RSP_STATUS code to exception mapping."""

    def test_map_rsp_status_resp_disabled(self):
        """Test mapping RSP_STATUS_RESP_DISABLED to TropicSquareResponseError."""
        exc = map_response_status_to_exception(RSP_STATUS_RESP_DISABLED)
        assert isinstance(exc, TropicSquareResponseError)
        assert "Response disabled" in str(exc)
        assert hex(RSP_STATUS_RESP_DISABLED) in str(exc)

    def test_map_rsp_status_hsk_error(self):
        """Test mapping RSP_STATUS_HSK_ERROR to TropicSquareHandshakeError."""
        exc = map_response_status_to_exception(RSP_STATUS_HSK_ERROR)
        assert isinstance(exc, TropicSquareHandshakeError)
        assert "Handshake error" in str(exc)
        assert hex(RSP_STATUS_HSK_ERROR) in str(exc)

    def test_map_rsp_status_no_session(self):
        """Test mapping RSP_STATUS_NO_SESSION to TropicSquareNoSession."""
        exc = map_response_status_to_exception(RSP_STATUS_NO_SESSION)
        assert isinstance(exc, TropicSquareNoSession)
        assert "No secure session established" in str(exc)
        assert hex(RSP_STATUS_NO_SESSION) in str(exc)

    def test_map_rsp_status_tag_error(self):
        """Test mapping RSP_STATUS_TAG_ERROR to TropicSquareTagError."""
        exc = map_response_status_to_exception(RSP_STATUS_TAG_ERROR)
        assert isinstance(exc, TropicSquareTagError)
        assert "Authentication tag error" in str(exc)
        assert hex(RSP_STATUS_TAG_ERROR) in str(exc)

    def test_map_rsp_status_crc_error(self):
        """Test mapping RSP_STATUS_CRC_ERROR to TropicSquareCRCError."""
        exc = map_response_status_to_exception(RSP_STATUS_CRC_ERROR)
        assert isinstance(exc, TropicSquareCRCError)
        assert "CRC validation failed" in str(exc)
        assert hex(RSP_STATUS_CRC_ERROR) in str(exc)

    def test_map_rsp_status_unknown_req(self):
        """Test mapping RSP_STATUS_UNKNOWN_REQ to TropicSquareInvalidCommandError."""
        exc = map_response_status_to_exception(RSP_STATUS_UNKNOWN_REQ)
        assert isinstance(exc, TropicSquareInvalidCommandError)
        assert "Unknown request" in str(exc)
        assert hex(RSP_STATUS_UNKNOWN_REQ) in str(exc)

    def test_map_rsp_status_gen_error(self):
        """Test mapping RSP_STATUS_GEN_ERROR to TropicSquareError."""
        exc = map_response_status_to_exception(RSP_STATUS_GEN_ERROR)
        assert isinstance(exc, TropicSquareError)
        assert "General error" in str(exc)
        assert hex(RSP_STATUS_GEN_ERROR) in str(exc)

    def test_map_rsp_status_no_response(self):
        """Test mapping RSP_STATUS_NO_RESPONSE to TropicSquareTimeoutError."""
        exc = map_response_status_to_exception(RSP_STATUS_NO_RESPONSE)
        assert isinstance(exc, TropicSquareTimeoutError)
        assert "No response from chip" in str(exc)
        assert hex(RSP_STATUS_NO_RESPONSE) in str(exc)

    def test_map_unknown_rsp_status(self):
        """Test mapping unknown RSP_STATUS to default TropicSquareError."""
        unknown_code = 0xAB
        exc = map_response_status_to_exception(unknown_code)
        assert isinstance(exc, TropicSquareError)
        assert "Unknown response error" in str(exc)
        assert hex(unknown_code) in str(exc)


class TestRaiseFunctions:
    """Test exception raising functions."""

    def test_raise_for_cmd_result_ok_does_not_raise(self):
        """Test that CMD_RESULT_OK does not raise exception."""
        try:
            raise_for_cmd_result(CMD_RESULT_OK)
        except Exception as e:
            pytest.fail(f"Should not raise exception for CMD_RESULT_OK, but raised: {e}")

    def test_raise_for_cmd_result_fail_raises(self):
        """Test that CMD_RESULT_FAIL raises exception."""
        with pytest.raises(TropicSquareCommandError) as exc_info:
            raise_for_cmd_result(CMD_RESULT_FAIL)
        assert "Command execution failed" in str(exc_info.value)

    def test_raise_for_cmd_result_unauthorized_raises(self):
        """Test that CMD_RESULT_UNAUTHORIZED raises exception."""
        with pytest.raises(TropicSquareUnauthorizedError) as exc_info:
            raise_for_cmd_result(CMD_RESULT_UNAUTHORIZED)
        assert "Command not authorized" in str(exc_info.value)

    def test_raise_for_cmd_result_memory_error_raises(self):
        """Test that memory error codes raise appropriate exceptions."""
        with pytest.raises(TropicSquareMemoryWriteError):
            raise_for_cmd_result(CMD_RESULT_MEM_WRITE_FAIL)

        with pytest.raises(TropicSquareMemorySlotExpiredError):
            raise_for_cmd_result(CMD_RESULT_MEM_SLOT_EXPIRED)

    def test_raise_for_response_status_ok_does_not_raise(self):
        """Test that valid RSP_STATUS codes do not raise exception."""
        valid_statuses = [
            RSP_STATUS_REQ_OK,
            RSP_STATUS_RES_OK,
            RSP_STATUS_REQ_CONT,
            RSP_STATUS_RES_CONT,
        ]

        for status in valid_statuses:
            try:
                raise_for_response_status(status)
            except Exception as e:
                pytest.fail(f"Should not raise exception for status {hex(status)}, but raised: {e}")

    def test_raise_for_response_status_error_raises(self):
        """Test that error RSP_STATUS codes raise exceptions."""
        with pytest.raises(TropicSquareResponseError):
            raise_for_response_status(RSP_STATUS_RESP_DISABLED)

        with pytest.raises(TropicSquareHandshakeError):
            raise_for_response_status(RSP_STATUS_HSK_ERROR)

        with pytest.raises(TropicSquareNoSession):
            raise_for_response_status(RSP_STATUS_NO_SESSION)

        with pytest.raises(TropicSquareTagError):
            raise_for_response_status(RSP_STATUS_TAG_ERROR)

        with pytest.raises(TropicSquareCRCError):
            raise_for_response_status(RSP_STATUS_CRC_ERROR)

        with pytest.raises(TropicSquareInvalidCommandError):
            raise_for_response_status(RSP_STATUS_UNKNOWN_REQ)

        with pytest.raises(TropicSquareError):
            raise_for_response_status(RSP_STATUS_GEN_ERROR)

        with pytest.raises(TropicSquareTimeoutError):
            raise_for_response_status(RSP_STATUS_NO_RESPONSE)

    def test_raise_for_unknown_response_status(self):
        """Test that unknown RSP_STATUS raises default exception."""
        with pytest.raises(TropicSquareError) as exc_info:
            raise_for_response_status(0xAB)
        assert "Unknown response error" in str(exc_info.value)


class TestExceptionMessageFormat:
    """Test exception message formatting."""

    def test_cmd_result_exception_contains_hex_code(self):
        """Test that CMD_RESULT exception messages contain hex code."""
        exc = map_cmd_result_to_exception(CMD_RESULT_FAIL)
        assert "0x3c" in str(exc)

    def test_rsp_status_exception_contains_hex_code(self):
        """Test that RSP_STATUS exception messages contain hex code."""
        exc = map_response_status_to_exception(RSP_STATUS_CRC_ERROR)
        assert "0x7c" in str(exc)

    def test_exception_message_format(self):
        """Test complete exception message format."""
        exc = map_cmd_result_to_exception(CMD_RESULT_UNAUTHORIZED)
        message = str(exc)

        # Should contain both description and hex code
        assert "Command not authorized" in message
        assert "(result: 0x1)" in message

    def test_response_exception_message_format(self):
        """Test complete response exception message format."""
        exc = map_response_status_to_exception(RSP_STATUS_NO_SESSION)
        message = str(exc)

        # Should contain both description and hex code
        assert "No secure session established" in message
        assert "(status: 0x7a)" in message
