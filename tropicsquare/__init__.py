# Version: 0.1

from tropicsquare.crc import CRC
from tropicsquare.constants import *
from tropicsquare.constants.chip_status import *
from tropicsquare.constants.get_info_req import *
from tropicsquare.constants.rsp_status import RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK, RSP_STATUS_REQ_CONT
from tropicsquare.constants.cmd_result import *
from tropicsquare.exceptions import *

from hashlib import sha256
from time import sleep

class TropicSquare:
    def __init__(self):
        self._secure_session = None
        self._certificate = None


    # TODO: Create L2 same parts more generic

    def _l2_get_info_req(self, object_id, req_data_chunk = GET_INFO_DATA_CHUNK_0_127):
        data = bytearray()
        data.extend(bytes(REQ_ID_GET_INFO_REQ))
        data.append(object_id)
        data.append(req_data_chunk)
        data.extend(CRC.crc16(data))

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

        calccrc = CRC.crc16(response + (data or b''))
        respcrc = self._spi.read(2)

        self._spi_cs(1)

        if respcrc != calccrc:
            raise TropicSquareCRCError("CRC mismatch")

        if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK]:
            raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))

        return data


    def _l2_handshake_req(self, ehpub, p_keyslot):
        data = bytearray()
        data.extend(bytes(REQ_ID_HANDSHARE_REQ))
        data.extend(ehpub)
        data.append(p_keyslot)
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        data = bytearray()
        data.extend(bytes(REQ_ID_GET_RESPONSE))

        sleep(0.1)

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

        calccrc = CRC.crc16(response + (data or b''))
        respcrc = self._spi.read(2)

        self._spi_cs(1)

        if respcrc != calccrc:
            raise TropicSquareCRCError("CRC mismatch")

        if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK]:
            raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))

        tsehpub = data[0:32]
        tsauth = data[32:48]

        return (tsehpub, tsauth)


    def _l2_get_log(self):
        data = bytearray()
        data.extend(bytes(REQ_ID_GET_LOG_REQ))
        data.extend(CRC.crc16(data))

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

        calccrc = CRC.crc16(response + (data or b''))
        respcrc = self._spi.read(2)

        self._spi_cs(1)

        if respcrc != calccrc:
            raise TropicSquareCRCError("CRC mismatch")

        if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK]:
            raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))

        return data


    def _l2_encrypted_command(self, command_size, command_ciphertext, command_tag):
        # 2 bytes: Command size
        length = COMMAND_SIZE_LEN + len(command_ciphertext) + len(command_tag)

        data = bytearray()
        data.extend(bytes(REQ_ID_ENCRYPTED_CMD_REQ))
        data.append(length)
        data.extend(command_size.to_bytes(COMMAND_SIZE_LEN, "little"))
        data.extend(command_ciphertext)
        data.extend(command_tag)
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        # Get response 1

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

        # TODO: Chunked response probably here may occur
        if response_length > 0:
            data = self._spi.read(response_length)
        else:
            data = None

        calccrc = CRC.crc16(response + (data or b''))
        respcrc = self._spi.read(2)

        self._spi_cs(1)

        if respcrc != calccrc:
            raise TropicSquareCRCError("CRC mismatch")

        if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK]:
            raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))


        # GET RESPONSE 2

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

        # TODO: Chunked response probably here may occur
        if response_length > 0:
            data = self._spi.read(response_length)
        else:
            data = None

        calccrc = CRC.crc16(response + (data or b''))
        respcrc = self._spi.read(2)

        self._spi_cs(1)

        if respcrc != calccrc:
            raise TropicSquareCRCError("CRC mismatch")

        if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK]:
            raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))

        command_size = int.from_bytes(data[0:2], "little")
        command_ciphertext = data[2:-16]
        command_tag = data[-16:]

        if command_size != len(command_ciphertext):
            raise TropicSquareError("Command size mismatch")


        return (command_ciphertext, command_tag)


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


    def start_secure_session(self, pkey_index, shpriv, shpub):
        ehpriv, ehpub = self._get_ephemeral_keypair()

        # Handshake request
        tsehpub, tsauth = self._l2_handshake_req(ehpub, pkey_index)

        # Calculation magic
        sha256hash = sha256()
        sha256hash.update(PROTOCOL_NAME)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(shpub)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(self.public_key)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(ehpub)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(pkey_index.to_bytes(1))

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(tsehpub)

        hash = sha256hash.digest()

        shared_secret_eh_tseh = self._x25519_exchange(ehpriv, tsehpub)
        shared_secret_sh_tseh = self._x25519_exchange(shpriv, tsehpub)
        shared_secret_eh_st = self._x25519_exchange(ehpriv, self.public_key)

        ck_hkdf_eh_tseh = self._hkdf(PROTOCOL_NAME, shared_secret_eh_tseh)
        ck_hkdf_sh_tseh = self._hkdf(ck_hkdf_eh_tseh, shared_secret_sh_tseh)
        ck_hkdf_cmdres, kauth = self._hkdf(ck_hkdf_sh_tseh, shared_secret_eh_st, 2)
        kcmd, kres = self._hkdf(ck_hkdf_cmdres, b'', 2)

        ciphertext_with_tag = self._aesgcm(kauth).encrypt(nonce=b'\x00'*12, data=b'', associated_data=hash)
        tag = ciphertext_with_tag[-16:]

        # Clear hanshake data
        shared_secret_eh_tseh = None
        shared_secret_sh_tseh = None
        shared_secret_eh_st = None

        ck_hkdf_eh_tseh = None
        ck_hkdf_sh_tseh = None
        ck_hkdf_cmdres = None
        kauth = None

        if tag != tsauth:
            raise TropicSquareError("Tauth mismatch, handshake failed")

        encrypt_key = self._aesgcm(kcmd)
        decrypt_key = self._aesgcm(kres)

        self._secure_session = [ encrypt_key, decrypt_key, 0 ]

        return True


    def get_log(self):
        log = b''
        while True:
            part = self._l2_get_log()
            if not part:
                break

            log += part

        return log.decode("utf-8")

    ###############
    # L3 Commands #
    ###############

    def ping(self, data):
        request_data = bytearray()
        request_data.append(CMD_ID_PING)
        request_data.extend(data)

        result = self._call_command(request_data)

        return result


    def get_random(self, length):
        request_data = bytearray()
        request_data.append(CMD_ID_RANDOM_VALUE)
        request_data.extend(length.to_bytes(1))

        result = self._call_command(request_data)

        return result[3:]


    def _l2_transfer(self, data):
        pass


    def _call_command(self, data):
        if self._secure_session is None:
            raise TropicSquareNoSession("Secure session not started")

        nonce = self._secure_session[2].to_bytes(12, "little")

        enc = self._secure_session[0].encrypt(nonce=nonce, data=data, associated_data=b'')
        ciphertext = enc[:-16]
        tag = enc[-16:]

        result_cipher, result_tag = self._l2_encrypted_command(len(ciphertext), ciphertext, tag)
        decrypted = self._secure_session[1].decrypt(nonce=nonce, data=result_cipher+result_tag, associated_data=b'')

        if decrypted[0] != CMD_RESULT_OK:
            raise TropicSquareError("Command failed with result: {}".format(hex(decrypted[0])))

        self._secure_session[2] += 1

        return decrypted[1:]


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


    def _get_ephemeral_keypair(self):
        raise NotImplementedError("Not implemented")


    def _hkdf(self, salt, shared_secret, length):
        raise NotImplementedError("Not implemented")


    def _x25519_exchange(self, private_bytes, public_bytes):
        raise NotImplementedError("Not implemented")


    def _aesgcm(self, key):
        raise NotImplementedError("Not implemented")
