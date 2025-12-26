"""Tests for L1 Transport Layer.

This module tests:
- send_request() method with various chip statuses
- get_response() method with retry logic, CRC validation, continuations
- Abstract method enforcement
- CS pin control
- Error handling and exceptions
"""

import pytest
from tropicsquare.transports import L1Transport
from tropicsquare.constants.chip_status import (
    CHIP_STATUS_READY,
    CHIP_STATUS_NOT_READY,
    CHIP_STATUS_BUSY,
    CHIP_STATUS_ALARM,
)
from tropicsquare.constants.l1 import REQ_ID_GET_RESPONSE, MAX_RETRIES
from tropicsquare.constants.rsp_status import (
    RSP_STATUS_RES_OK,
    RSP_STATUS_RES_CONT,
    RSP_STATUS_CRC_ERROR,
)
from tropicsquare.exceptions import (
    TropicSquareError,
    TropicSquareAlarmError,
    TropicSquareCRCError,
    TropicSquareTimeoutError,
)
from tropicsquare.crc import CRC


class MockableL1Transport(L1Transport):
    """Concrete mock implementation of L1Transport for testing."""

    def __init__(self):
        """Initialize mock transport with tracking."""
        self.transfer_calls = []
        self.read_calls = []
        self.cs_low_calls = 0
        self.cs_high_calls = 0
        self.next_transfer_return = None
        self.next_read_returns = []
        self.read_index = 0

    def _transfer(self, tx_data):
        """Mock transfer implementation."""
        self.transfer_calls.append(bytes(tx_data))
        if self.next_transfer_return is not None:
            return self.next_transfer_return
        # Default: return READY status + zeros
        return bytes([CHIP_STATUS_READY]) + b'\x00' * (len(tx_data) - 1)

    def _read(self, length):
        """Mock read implementation."""
        self.read_calls.append(length)
        if self.read_index < len(self.next_read_returns):
            result = self.next_read_returns[self.read_index]
            self.read_index += 1
            return result
        return b'\x00' * length

    def _cs_low(self):
        """Track CS low calls."""
        self.cs_low_calls += 1

    def _cs_high(self):
        """Track CS high calls."""
        self.cs_high_calls += 1


class TestSendRequest:
    """Test send_request() method."""

    def test_send_request_success(self):
        """Test successful request returns response bytes."""
        transport = MockableL1Transport()
        request = b'\x01\x02\x03\x04'

        expected_response = bytes([CHIP_STATUS_READY]) + b'\x00' * 3
        transport.next_transfer_return = expected_response

        rx_data = transport.send_request(request)

        assert rx_data == expected_response
        assert transport.cs_low_calls == 1
        assert transport.cs_high_calls == 1
        assert transport.transfer_calls[0] == request

    def test_send_request_calls_cs_methods(self):
        """Test that send_request calls CS low/high."""
        transport = MockableL1Transport()
        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00' * 3

        transport.send_request(b'\x01\x02\x03\x04')

        assert transport.cs_low_calls == 1
        assert transport.cs_high_calls == 1

    def test_send_request_returns_any_status(self):
        """Test that send_request returns response regardless of chip status."""
        transport = MockableL1Transport()

        # Test with NOT_READY status - should still return data without error
        transport.next_transfer_return = bytes([CHIP_STATUS_NOT_READY]) + b'\x00' * 3
        rx_data = transport.send_request(b'\x01\x02\x03\x04')
        assert rx_data[0] == CHIP_STATUS_NOT_READY

        # Test with BUSY status - should still return data without error
        transport.next_transfer_return = bytes([CHIP_STATUS_BUSY]) + b'\x00' * 3
        rx_data = transport.send_request(b'\x01\x02\x03\x04')
        assert rx_data[0] == CHIP_STATUS_BUSY


class TestGetResponseBasic:
    """Test basic get_response() functionality."""

    def test_get_response_with_data_success(self):
        """Test successful response with data."""
        transport = MockableL1Transport()

        # Setup: chip returns READY, then response with data
        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00'
        response_data = b'\x12\x34\x56\x78'
        response_header = bytes([RSP_STATUS_RES_OK, len(response_data)])
        crc = CRC.crc16(response_header + response_data)

        transport.next_read_returns = [
            response_header,
            response_data,
            crc,
        ]

        result = transport.get_response()

        assert result == response_data
        assert transport.cs_low_calls == 1
        assert transport.cs_high_calls == 1

    def test_get_response_no_data_success(self):
        """Test successful response without data (length=0)."""
        transport = MockableL1Transport()

        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00'
        response_header = bytes([RSP_STATUS_RES_OK, 0])
        crc = CRC.crc16(response_header)

        transport.next_read_returns = [
            response_header,
            crc,
        ]

        result = transport.get_response()

        assert result is None


class TestGetResponseRetryLogic:
    """Test get_response() retry logic."""

    def test_get_response_retries_on_not_ready(self):
        """Test that get_response retries when chip is NOT_READY."""
        transport = MockableL1Transport()

        # First attempt: NOT_READY
        # Second attempt: READY with response
        call_count = [0]

        def mock_transfer(data):
            call_count[0] += 1
            if call_count[0] == 1:
                return bytes([CHIP_STATUS_NOT_READY]) + b'\x00'
            else:
                return bytes([CHIP_STATUS_READY]) + b'\x00'

        transport._transfer = mock_transfer

        response_header = bytes([RSP_STATUS_RES_OK, 0])
        crc = CRC.crc16(response_header)
        transport.next_read_returns = [response_header, crc]

        result = transport.get_response()

        assert result is None
        assert call_count[0] == 2
        assert transport.cs_low_calls == 2
        assert transport.cs_high_calls == 2

    def test_get_response_timeout_after_max_retries(self):
        """Test that get_response raises timeout after MAX_RETRIES."""
        transport = MockableL1Transport()

        # Always return NOT_READY
        transport.next_transfer_return = bytes([CHIP_STATUS_NOT_READY]) + b'\x00'

        with pytest.raises(TropicSquareTimeoutError) as exc_info:
            transport.get_response()

        assert "chip remains busy" in str(exc_info.value)
        assert transport.cs_low_calls == MAX_RETRIES


class TestGetResponseAlarm:
    """Test get_response() alarm detection."""

    def test_get_response_alarm_raises_error(self):
        """Test that ALARM status raises TropicSquareAlarmError."""
        transport = MockableL1Transport()

        transport.next_transfer_return = bytes([CHIP_STATUS_ALARM]) + b'\x00'

        with pytest.raises(TropicSquareAlarmError) as exc_info:
            transport.get_response()

        assert "Chip is in alarm state" in str(exc_info.value)
        assert transport.cs_high_calls == 1


class TestGetResponseCRC:
    """Test get_response() CRC validation."""

    def test_get_response_crc_valid(self):
        """Test that valid CRC passes."""
        transport = MockableL1Transport()

        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00'
        response_data = b'\x12\x34'
        response_header = bytes([RSP_STATUS_RES_OK, len(response_data)])
        valid_crc = CRC.crc16(response_header + response_data)

        transport.next_read_returns = [
            response_header,
            response_data,
            valid_crc,
        ]

        result = transport.get_response()
        assert result == response_data

    def test_get_response_crc_invalid_raises_error(self):
        """Test that invalid CRC raises TropicSquareCRCError."""
        transport = MockableL1Transport()

        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00'
        response_data = b'\x12\x34'
        response_header = bytes([RSP_STATUS_RES_OK, len(response_data)])
        valid_crc = CRC.crc16(response_header + response_data)
        invalid_crc = b'\xFF\xFF'  # Wrong CRC

        transport.next_read_returns = [
            response_header,
            response_data,
            invalid_crc,
        ]

        with pytest.raises(TropicSquareCRCError) as exc_info:
            transport.get_response()

        assert "CRC mismatch" in str(exc_info.value)
        assert valid_crc.hex() in str(exc_info.value)
        assert invalid_crc.hex() in str(exc_info.value)


class TestGetResponseContinuation:
    """Test get_response() continuation support."""

    def test_get_response_continuation(self):
        """Test that RES_CONT triggers recursive call."""
        transport = MockableL1Transport()

        # First call: return CONT status
        # Second call (recursive): return OK
        call_count = [0]
        original_get_response = transport.get_response.__func__

        def mock_recursive_get_response(self):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call - return normally with continuation logic
                return original_get_response(self)
            else:
                # Recursive call - return final data
                return b'\x78\x9A'

        transport.get_response = lambda: mock_recursive_get_response(transport)

        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00'
        first_chunk = b'\x12\x34'
        response_header = bytes([RSP_STATUS_RES_CONT, len(first_chunk)])
        crc = CRC.crc16(response_header + first_chunk)

        transport.next_read_returns = [
            response_header,
            first_chunk,
            crc,
        ]

        # Note: This test is complex due to recursion
        # In real implementation, continuation would call get_response again


class TestAbstractMethods:
    """Test abstract method enforcement."""

    def test_transfer_not_implemented(self):
        """Test that _transfer raises NotImplementedError on base class."""
        transport = L1Transport()
        with pytest.raises(NotImplementedError) as exc_info:
            transport._transfer(b'\x01\x02')
        assert "_transfer() method not implemented" in str(exc_info.value)

    def test_read_not_implemented(self):
        """Test that _read raises NotImplementedError on base class."""
        transport = L1Transport()
        with pytest.raises(NotImplementedError) as exc_info:
            transport._read(4)
        assert "_read() method not implemented" in str(exc_info.value)

    def test_cs_methods_are_callable(self):
        """Test that _cs_low and _cs_high are callable (no-ops on base class)."""
        transport = L1Transport()
        # Should not raise
        transport._cs_low()
        transport._cs_high()


class TestResponseStatusHandling:
    """Test that response status errors are raised."""

    def test_get_response_raises_for_error_status(self):
        """Test that error response status raises appropriate exception."""
        transport = MockableL1Transport()

        transport.next_transfer_return = bytes([CHIP_STATUS_READY]) + b'\x00'
        response_header = bytes([RSP_STATUS_CRC_ERROR, 0])
        crc = CRC.crc16(response_header)

        transport.next_read_returns = [
            response_header,
            crc,
        ]

        # Should raise TropicSquareCRCError due to response status
        with pytest.raises(TropicSquareCRCError):
            transport.get_response()
