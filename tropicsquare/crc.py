# Implement CRC16 checksum

class CRC:
    CRC16_POLYNOMIAL = 0x8005
    CRC16_INITIAL_VAL = 0x0000
    CRC16_FINAL_XOR_VALUE = 0x0000


    @classmethod
    def crc16(cls, data: bytes) -> bytes:
        """Compute the CRC16 value for the given byte sequence."""
        crc = cls.CRC16_INITIAL_VAL
        for byte in data:
            crc = cls._crc16_byte(byte, crc)
        crc ^= cls.CRC16_FINAL_XOR_VALUE

        return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


    @classmethod
    def _crc16_byte(cls, data: int, crc: int) -> int:
        """Process one byte of data into the CRC."""
        crc ^= data << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ cls.CRC16_POLYNOMIAL
            else:
                crc <<= 1
            crc &= 0xFFFF
        return crc
