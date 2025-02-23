# Version: 0.1

from .crc16 import CRC16
from tropicsquare.constants import *
from tropicsquare.constants.get_info_req import *


class TropicSquare:
    def __init__(self):
        self._crc16 = CRC16()
        self._secure_session = None


    @property
    def chipid(self):
        data = bytearray()
        data.extend(bytes(REQ_ID_GET_INFO_REQ))
        data.append(GET_INFO_CHIPID)
        data.append(GET_INFO_DATA_CHUNK_0_127)
        data.extend(self._crc16.crc16(data))
        return data


    @property
    def riscv_fw_version(self):
        data = bytearray()
        data.extend(bytes(REQ_ID_GET_INFO_REQ))
        data.append(GET_INFO_RISCV_FW_VERSION)
        data.append(GET_INFO_DATA_CHUNK_0_127)
        data.extend(self._crc16.crc16(data))
        return data


    def start_secure_session(self, pubkey, privkey):
        raise NotImplementedError("Not implemented yet")


    def ping(self, data):
        if self._secure_session is None:
            raise Exception("Secure session not started")

        raise NotImplementedError("Not implemented yet")


    def get_random(self):
        if self._secure_session is None:
            raise Exception("Secure session not started")

        raise NotImplementedError("Not implemented yet")


    def _l2_transfer(self, data):
        pass


    def _spi_cs(self, value):
        # This must be implemented by the user in child class
        raise NotImplementedError("Not implemented")


    def _spi_write(self, data):
        # This must be implemented by the user in child class
        raise NotImplementedError("Not implemented")


    def _spi_read(self, len: int) -> bytes:
        raise NotImplementedError("Not implemented")


    def _spi_readinto(self, buffer: bytearray):
        raise NotImplementedError("Not implemented")


    def _spi_write_readinto(self, tx_buffer, rx_buffer: bytearray):
        raise NotImplementedError("Not implemented")
