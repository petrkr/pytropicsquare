"""Tests for TropicSquare exception hierarchy.

This module tests:
- Exception class hierarchy and inheritance
- Exception instantiation and messages
- Exception catching and raising
- Import accessibility
"""

import pytest
from tropicsquare.exceptions import (
    TropicSquareError,
    TropicSquareCRCError,
    TropicSquareNoSession,
    TropicSquareTimeoutError,
    TropicSquareAlarmError,
    TropicSquareCommandError,
    TropicSquareUnauthorizedError,
    TropicSquareInvalidCommandError,
    TropicSquareMemoryError,
    TropicSquareMemoryWriteError,
    TropicSquareMemorySlotExpiredError,
    TropicSquareECCError,
    TropicSquareECCInvalidKeyError,
    TropicSquareCounterError,
    TropicSquareCounterUpdateError,
    TropicSquareCounterInvalidError,
    TropicSquareSessionError,
    TropicSquareHandshakeError,
    TropicSquareTagError,
    TropicSquareResponseError,
)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_base_exception_is_exception(self):
        """Test that TropicSquareError inherits from Exception."""
        assert issubclass(TropicSquareError, Exception)
        exc = TropicSquareError()
        assert isinstance(exc, Exception)

    def test_crc_error_inheritance(self):
        """Test TropicSquareCRCError inherits from TropicSquareError."""
        assert issubclass(TropicSquareCRCError, TropicSquareError)
        exc = TropicSquareCRCError()
        assert isinstance(exc, TropicSquareError)
        assert isinstance(exc, Exception)

    def test_no_session_inheritance(self):
        """Test TropicSquareNoSession inherits from TropicSquareError."""
        assert issubclass(TropicSquareNoSession, TropicSquareError)
        exc = TropicSquareNoSession()
        assert isinstance(exc, TropicSquareError)

    def test_timeout_error_inheritance(self):
        """Test TropicSquareTimeoutError inherits from TropicSquareError."""
        assert issubclass(TropicSquareTimeoutError, TropicSquareError)
        exc = TropicSquareTimeoutError()
        assert isinstance(exc, TropicSquareError)

    def test_alarm_error_inheritance(self):
        """Test TropicSquareAlarmError inherits from TropicSquareError."""
        assert issubclass(TropicSquareAlarmError, TropicSquareError)
        exc = TropicSquareAlarmError()
        assert isinstance(exc, TropicSquareError)

    def test_command_error_inheritance(self):
        """Test TropicSquareCommandError inherits from TropicSquareError."""
        assert issubclass(TropicSquareCommandError, TropicSquareError)
        exc = TropicSquareCommandError()
        assert isinstance(exc, TropicSquareError)

    def test_unauthorized_error_inheritance(self):
        """Test TropicSquareUnauthorizedError inherits from TropicSquareCommandError."""
        assert issubclass(TropicSquareUnauthorizedError, TropicSquareCommandError)
        assert issubclass(TropicSquareUnauthorizedError, TropicSquareError)
        exc = TropicSquareUnauthorizedError()
        assert isinstance(exc, TropicSquareCommandError)
        assert isinstance(exc, TropicSquareError)

    def test_invalid_command_error_inheritance(self):
        """Test TropicSquareInvalidCommandError inherits from TropicSquareCommandError."""
        assert issubclass(TropicSquareInvalidCommandError, TropicSquareCommandError)
        exc = TropicSquareInvalidCommandError()
        assert isinstance(exc, TropicSquareCommandError)

    def test_memory_error_inheritance(self):
        """Test TropicSquareMemoryError inherits from TropicSquareCommandError."""
        assert issubclass(TropicSquareMemoryError, TropicSquareCommandError)
        exc = TropicSquareMemoryError()
        assert isinstance(exc, TropicSquareCommandError)

    def test_memory_write_error_inheritance(self):
        """Test TropicSquareMemoryWriteError inherits from TropicSquareMemoryError."""
        assert issubclass(TropicSquareMemoryWriteError, TropicSquareMemoryError)
        assert issubclass(TropicSquareMemoryWriteError, TropicSquareCommandError)
        exc = TropicSquareMemoryWriteError()
        assert isinstance(exc, TropicSquareMemoryError)
        assert isinstance(exc, TropicSquareCommandError)

    def test_memory_slot_expired_error_inheritance(self):
        """Test TropicSquareMemorySlotExpiredError inherits from TropicSquareMemoryError."""
        assert issubclass(TropicSquareMemorySlotExpiredError, TropicSquareMemoryError)
        exc = TropicSquareMemorySlotExpiredError()
        assert isinstance(exc, TropicSquareMemoryError)

    def test_ecc_error_inheritance(self):
        """Test TropicSquareECCError inherits from TropicSquareCommandError."""
        assert issubclass(TropicSquareECCError, TropicSquareCommandError)
        exc = TropicSquareECCError()
        assert isinstance(exc, TropicSquareCommandError)

    def test_ecc_invalid_key_error_inheritance(self):
        """Test TropicSquareECCInvalidKeyError inherits from TropicSquareECCError."""
        assert issubclass(TropicSquareECCInvalidKeyError, TropicSquareECCError)
        assert issubclass(TropicSquareECCInvalidKeyError, TropicSquareCommandError)
        exc = TropicSquareECCInvalidKeyError()
        assert isinstance(exc, TropicSquareECCError)
        assert isinstance(exc, TropicSquareCommandError)

    def test_counter_error_inheritance(self):
        """Test TropicSquareCounterError inherits from TropicSquareCommandError."""
        assert issubclass(TropicSquareCounterError, TropicSquareCommandError)
        exc = TropicSquareCounterError()
        assert isinstance(exc, TropicSquareCommandError)

    def test_counter_update_error_inheritance(self):
        """Test TropicSquareCounterUpdateError inherits from TropicSquareCounterError."""
        assert issubclass(TropicSquareCounterUpdateError, TropicSquareCounterError)
        exc = TropicSquareCounterUpdateError()
        assert isinstance(exc, TropicSquareCounterError)

    def test_counter_invalid_error_inheritance(self):
        """Test TropicSquareCounterInvalidError inherits from TropicSquareCounterError."""
        assert issubclass(TropicSquareCounterInvalidError, TropicSquareCounterError)
        exc = TropicSquareCounterInvalidError()
        assert isinstance(exc, TropicSquareCounterError)

    def test_session_error_inheritance(self):
        """Test TropicSquareSessionError inherits from TropicSquareError."""
        assert issubclass(TropicSquareSessionError, TropicSquareError)
        exc = TropicSquareSessionError()
        assert isinstance(exc, TropicSquareError)

    def test_handshake_error_inheritance(self):
        """Test TropicSquareHandshakeError inherits from TropicSquareSessionError."""
        assert issubclass(TropicSquareHandshakeError, TropicSquareSessionError)
        assert issubclass(TropicSquareHandshakeError, TropicSquareError)
        exc = TropicSquareHandshakeError()
        assert isinstance(exc, TropicSquareSessionError)
        assert isinstance(exc, TropicSquareError)

    def test_tag_error_inheritance(self):
        """Test TropicSquareTagError inherits from TropicSquareSessionError."""
        assert issubclass(TropicSquareTagError, TropicSquareSessionError)
        exc = TropicSquareTagError()
        assert isinstance(exc, TropicSquareSessionError)

    def test_response_error_inheritance(self):
        """Test TropicSquareResponseError inherits from TropicSquareError."""
        assert issubclass(TropicSquareResponseError, TropicSquareError)
        exc = TropicSquareResponseError()
        assert isinstance(exc, TropicSquareError)


class TestExceptionMessages:
    """Test exception message handling."""

    def test_exception_with_message(self):
        """Test exception can be created with custom message."""
        msg = "Custom error message"
        exc = TropicSquareError(msg)
        assert str(exc) == msg

    def test_crc_error_with_message(self):
        """Test CRC error can be created with custom message."""
        msg = "CRC validation failed"
        exc = TropicSquareCRCError(msg)
        assert str(exc) == msg

    def test_timeout_error_with_message(self):
        """Test timeout error can be created with custom message."""
        msg = "Chip communication timeout after 5 retries"
        exc = TropicSquareTimeoutError(msg)
        assert str(exc) == msg

    def test_memory_error_with_message(self):
        """Test memory error can be created with custom message."""
        msg = "Memory slot write failed"
        exc = TropicSquareMemoryWriteError(msg)
        assert str(exc) == msg

    def test_exception_without_message(self):
        """Test exception can be created without message."""
        exc = TropicSquareError()
        assert str(exc) == ""


class TestExceptionRaisingAndCatching:
    """Test exception raising and catching behavior."""

    def test_raise_and_catch_base_exception(self):
        """Test raising and catching base exception."""
        with pytest.raises(TropicSquareError) as exc_info:
            raise TropicSquareError("Test error")
        assert str(exc_info.value) == "Test error"

    def test_catch_derived_as_base(self):
        """Test that derived exception can be caught as base exception."""
        with pytest.raises(TropicSquareError):
            raise TropicSquareCRCError("CRC failed")

    def test_catch_command_error_as_base(self):
        """Test that command error can be caught as base exception."""
        with pytest.raises(TropicSquareError):
            raise TropicSquareCommandError("Command failed")

    def test_catch_memory_error_as_command_error(self):
        """Test that memory error can be caught as command error."""
        with pytest.raises(TropicSquareCommandError):
            raise TropicSquareMemoryError("Memory operation failed")

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(TropicSquareTimeoutError) as exc_info:
            raise TropicSquareTimeoutError("Timeout occurred")
        assert isinstance(exc_info.value, TropicSquareTimeoutError)

    def test_exception_not_caught_by_unrelated_type(self):
        """Test that exception is not caught by unrelated type."""
        with pytest.raises(TropicSquareCRCError):
            try:
                raise TropicSquareCRCError("CRC error")
            except TropicSquareTimeoutError:
                pytest.fail("Should not catch CRC error as timeout error")


class TestExceptionImports:
    """Test that all exceptions are importable."""

    def test_all_exceptions_importable(self):
        """Test that all exception classes are importable from package."""
        from tropicsquare import exceptions

        # Base exceptions
        assert hasattr(exceptions, 'TropicSquareError')
        assert hasattr(exceptions, 'TropicSquareCRCError')
        assert hasattr(exceptions, 'TropicSquareNoSession')

        # Communication errors
        assert hasattr(exceptions, 'TropicSquareTimeoutError')
        assert hasattr(exceptions, 'TropicSquareAlarmError')

        # Command errors
        assert hasattr(exceptions, 'TropicSquareCommandError')
        assert hasattr(exceptions, 'TropicSquareUnauthorizedError')
        assert hasattr(exceptions, 'TropicSquareInvalidCommandError')

        # Memory errors
        assert hasattr(exceptions, 'TropicSquareMemoryError')
        assert hasattr(exceptions, 'TropicSquareMemoryWriteError')
        assert hasattr(exceptions, 'TropicSquareMemorySlotExpiredError')

        # ECC errors
        assert hasattr(exceptions, 'TropicSquareECCError')
        assert hasattr(exceptions, 'TropicSquareECCInvalidKeyError')

        # Counter errors
        assert hasattr(exceptions, 'TropicSquareCounterError')
        assert hasattr(exceptions, 'TropicSquareCounterUpdateError')
        assert hasattr(exceptions, 'TropicSquareCounterInvalidError')

        # Session errors
        assert hasattr(exceptions, 'TropicSquareSessionError')
        assert hasattr(exceptions, 'TropicSquareHandshakeError')
        assert hasattr(exceptions, 'TropicSquareTagError')

        # Response errors
        assert hasattr(exceptions, 'TropicSquareResponseError')

    def test_exception_class_attributes(self):
        """Test that exception classes have correct attributes."""
        # Check docstrings exist
        assert TropicSquareError.__doc__ is not None
        assert TropicSquareCRCError.__doc__ is not None
        assert TropicSquareNoSession.__doc__ is not None

        # Check they are classes
        assert isinstance(TropicSquareError, type)
        assert isinstance(TropicSquareCRCError, type)
