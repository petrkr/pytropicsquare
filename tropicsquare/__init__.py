# Version: 0.1

from .crc16 import CRC16
from tropicsquare.constants import *
from tropicsquare.constants.chip_status import *
from tropicsquare.constants.get_info_req import *
from tropicsquare.constants.rsp_status import RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK
from tropicsquare.exceptions import *


class TropicSquare:
    def __init__(self):
        self._crc16 = CRC16()
        self._secure_session = None
        self._certificate = None


    def _l2_get_info_req(self, object_id, req_data_chunk = GET_INFO_DATA_CHUNK_0_127):
        data = bytearray()
        data.extend(bytes(REQ_ID_GET_INFO_REQ))
        data.append(object_id)
        data.append(req_data_chunk)
        data.extend(self._crc16.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        data = bytearray()
        data.extend(bytes(REQ_ID_GET_RESPONSE))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)

        chip_status = data[0]
        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        response = self._spi.read(2)

        response_status = response[0]
        response_length = response[1]

        if response_length > 0:
            data = self._spi.read(response_length)
        else:
            data = None

        calccrc = self._crc16.crc16(response + (data or b''))
        respcrc = self._spi.read(2)

        self._spi_cs(1)

        if respcrc != calccrc:
            raise TropicSquareCRCError("CRC mismatch")

        if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK]:
            raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))

        return data


    @property
    def certificate(self):
        if self._certificate:
            return self._certificate

        data = self._l2_get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_0_127)
        data += self._l2_get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_128_255)
        data += self._l2_get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_256_383)
        data += self._l2_get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_384_511)

        # TODO: Figure out what are that 10 bytes at the beginning
        # 2 bytes: unknown
        # 2 bytes (big-endian): length of the certificate
        # 6 bytes: unknown
        lenght = int.from_bytes(data[2:4], "big")
        self._certificate = data[10:10+lenght]
        return self._certificate


    @property
    def public_key(self):
        if self._certificate is None:
            cert = self.certificate
        else :
            cert = self._certificate

        # Find signature for X25519 public key
        # 0x65, 0x6e, 0x03 and 0x21
        def _parse_public_key(cert):
            for i in range(len(cert)):
                if cert[i] == 0x65:
                    if cert[i+1] == 0x6e and \
                       cert[i+2] == 0x03 and \
                       cert[i+3] == 0x21:
                        # Found it
                        # Plus 5 bytes to skip the signature
                        return cert[i+5:i+5+32]

        return _parse_public_key(cert)


    @property
    def chipid(self):
        return self._l2_get_info_req(GET_INFO_CHIPID)


    @property
    def riscv_fw_version(self):
        return self._l2_get_info_req(GET_INFO_RISCV_FW_VERSION)


    @property
    def spect_fw_version(self):
        return self._l2_get_info_req(GET_INFO_SPECT_FW_VERSION)


    @property
    def fw_bank(self):
        return self._l2_get_info_req(GET_INFO_FW_BANK)


    def start_secure_session(self, stpub, pkey_index, shpriv, shpub):
        raise NotImplementedError("Not implemented yet")


    def ping(self, data):
        if self._secure_session is None:
            raise TropicSquareNoSession("Secure session not started")

        raise NotImplementedError("Not implemented yet")


    def get_random(self):
        if self._secure_session is None:
            raise TropicSquareNoSession("Secure session not started")

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
