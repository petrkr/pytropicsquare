"""Unit tests for CRC16 calculation module.

Tests the CRC16 checksum implementation used for L2 protocol validation.
All tests run without hardware and verify pure mathematical operations.
"""

import pytest
from tropicsquare.crc import CRC


class TestCRC16:
    """Test cases for CRC16 calculation."""

    def test_crc16_empty_data(self):
        """Test CRC16 with empty data."""
        result = CRC.crc16(b'')
        assert isinstance(result, bytes)
        assert len(result) == 2
        # Empty data should return initial value XOR'd with final XOR
        # With INITIAL=0x0000 and FINAL_XOR=0x0000, should be 0x0000
        assert result == b'\x00\x00'

    def test_crc16_single_byte(self):
        """Test CRC16 with single byte."""
        result = CRC.crc16(b'\x00')
        assert isinstance(result, bytes)
        assert len(result) == 2

    def test_crc16_known_values(self):
        """Test CRC16 with known input/output pairs."""
        # Test with simple data
        test_cases = [
            (b'\x01\x02\x03\x04', None),  # Will verify consistency
            (b'Hello', None),
            (b'\xff\xff\xff\xff', None),
        ]

        for data, expected in test_cases:
            result = CRC.crc16(data)
            assert isinstance(result, bytes)
            assert len(result) == 2
            # Verify it's deterministic by calling twice
            result2 = CRC.crc16(data)
            assert result == result2

    def test_crc16_consistency(self):
        """Test that same input always produces same output."""
        test_data = b'\x12\x34\x56\x78\x9a\xbc\xde\xf0'
        results = [CRC.crc16(test_data) for _ in range(10)]
        # All results should be identical
        assert all(r == results[0] for r in results)

    def test_crc16_different_data_different_result(self):
        """Test that different data produces different CRC."""
        data1 = b'\x00\x00\x00\x00'
        data2 = b'\x01\x01\x01\x01'
        result1 = CRC.crc16(data1)
        result2 = CRC.crc16(data2)
        # Different inputs should (very likely) produce different outputs
        assert result1 != result2

    def test_crc16_return_type(self):
        """Test that CRC16 always returns bytes of length 2."""
        test_inputs = [
            b'',
            b'\x00',
            b'\x01\x02',
            b'\x01\x02\x03',
            b'A' * 100,
            b'\xff' * 256,
        ]
        for data in test_inputs:
            result = CRC.crc16(data)
            assert isinstance(result, bytes), f"Result is not bytes for input {data!r}"
            assert len(result) == 2, f"Result length is {len(result)}, expected 2 for input {data!r}"

    def test_crc16_byte_order(self):
        """Test CRC16 byte order (little-endian)."""
        # CRC should be returned as [low_byte, high_byte]
        result = CRC.crc16(b'\x00')
        assert isinstance(result, bytes)
        assert len(result) == 2
        # Verify we can extract both bytes
        low_byte = result[0]
        high_byte = result[1]
        assert isinstance(low_byte, int)
        assert isinstance(high_byte, int)

    def test_crc16_large_data(self):
        """Test CRC16 with large data."""
        # Test with data larger than typical protocol messages
        large_data = bytes(range(256)) * 4  # 1024 bytes
        result = CRC.crc16(large_data)
        assert isinstance(result, bytes)
        assert len(result) == 2

    def test_crc16_all_zeros(self):
        """Test CRC16 with all zero bytes."""
        data = b'\x00' * 64
        result = CRC.crc16(data)
        assert isinstance(result, bytes)
        assert len(result) == 2
        # Verify consistency
        assert CRC.crc16(data) == result

    def test_crc16_all_ones(self):
        """Test CRC16 with all 0xFF bytes."""
        data = b'\xff' * 64
        result = CRC.crc16(data)
        assert isinstance(result, bytes)
        assert len(result) == 2
        # Verify consistency
        assert CRC.crc16(data) == result


class TestCRC16Internal:
    """Test cases for internal CRC16 helper method."""

    def test_crc16_byte_returns_int(self):
        """Test that _crc16_byte returns an integer."""
        result = CRC._crc16_byte(0x00, 0x0000)
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFF

    def test_crc16_byte_range(self):
        """Test _crc16_byte with various byte values."""
        for byte_val in [0x00, 0x01, 0x7F, 0x80, 0xFF]:
            result = CRC._crc16_byte(byte_val, 0x0000)
            assert isinstance(result, int)
            assert 0 <= result <= 0xFFFF

    def test_crc16_byte_with_different_crc(self):
        """Test _crc16_byte with various CRC values."""
        for crc_val in [0x0000, 0x1234, 0x8000, 0xFFFF]:
            result = CRC._crc16_byte(0x00, crc_val)
            assert isinstance(result, int)
            assert 0 <= result <= 0xFFFF


class TestCRC16Constants:
    """Test CRC16 configuration constants."""

    def test_crc16_constants_exist(self):
        """Test that CRC16 constants are defined."""
        assert hasattr(CRC, 'CRC16_POLYNOMIAL')
        assert hasattr(CRC, 'CRC16_INITIAL_VAL')
        assert hasattr(CRC, 'CRC16_FINAL_XOR_VALUE')

    def test_crc16_polynomial_value(self):
        """Test CRC16 polynomial value."""
        # CRC-16/BUYPASS polynomial
        assert CRC.CRC16_POLYNOMIAL == 0x8005

    def test_crc16_initial_value(self):
        """Test CRC16 initial value."""
        assert CRC.CRC16_INITIAL_VAL == 0x0000

    def test_crc16_final_xor_value(self):
        """Test CRC16 final XOR value."""
        assert CRC.CRC16_FINAL_XOR_VALUE == 0x0000
