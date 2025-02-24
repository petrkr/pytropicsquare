# Version: 0.1

from .crc16 import CRC16
from tropicsquare.constants import *
from tropicsquare.constants.chip_status import *
from tropicsquare.constants.get_info_req import *
from tropicsquare.constants.rsp_status import RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK
from tropicsquare.exceptions import *

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from hashlib import sha256
from time import sleep

class TropicSquare:
    def __init__(self):
        self._crc16 = CRC16()
        self._secure_session = None
        self._certificate = None


    # TODO: Create L2 same parts more generic

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


    def _l2_handshake_req(self, ehpub, p_keyslot):
        data = bytearray()
        data.extend(bytes(REQ_ID_HANDSHARE_REQ))
        data.extend(ehpub)
        data.append(p_keyslot)
        data.extend(self._crc16.crc16(data))

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

        calccrc = self._crc16.crc16(response + (data or b''))
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
        ehpriv, ehpub = self._get_ephemeral_keypair()

        print("STPub: {}".format(stpub.hex()))
        print("PKey Index: {}".format(pkey_index))
        print("SHPriv: {}".format(shpriv.hex()))
        print("SHPub: {}".format(shpub.hex()))
        print("EHPriv: {}".format(ehpriv.hex()))
        print("EHPub: {}".format(ehpub.hex()))

        # Handshake request
        tsehpub, tsauth = self._l2_handshake_req(ehpub, pkey_index)

        print("TSEHPub: {}".format(tsehpub.hex()))
        print("TSAuth: {}".format(tsauth.hex()))

        # Calculation magic

        sha256hash = sha256()
        sha256hash.update(PROTOCOL_NAME)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(shpub)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(stpub)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(ehpub)

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(pkey_index.to_bytes(1, "big"))

        sha256hash = sha256(sha256hash.digest())
        sha256hash.update(tsehpub)

        print ("SHA256: {}".format(sha256hash.hexdigest()))

        # TODO: Implement for platform specific
        ehpriv = X25519PrivateKey.from_private_bytes(ehpriv)
        shpriv = X25519PrivateKey.from_private_bytes(shpriv)

        shared_secret_eh_tseh = ehpriv.exchange(X25519PublicKey.from_public_bytes(tsehpub))
        print("Shared secret EH vs TSEH: {}".format(shared_secret_eh_tseh.hex()))

        shared_secret_sh_tseh = shpriv.exchange(X25519PublicKey.from_public_bytes(tsehpub))
        print("Shared secret SH vs ST: {}".format(shared_secret_sh_tseh.hex()))

        shared_secret_eh_st = ehpriv.exchange(X25519PublicKey.from_public_bytes(stpub))
        print("Shared secret EH vs ST: {}".format(shared_secret_eh_st.hex()))


        ck_hkdf_eh_tseh = HKDF(algorithm=hashes.SHA256(),
                     length=32,
                     salt=PROTOCOL_NAME,
                     info=None).derive(shared_secret_eh_tseh)

        ck_hkdf_sh_tseh = HKDF(algorithm=hashes.SHA256(),
                     length=32,
                     salt=ck_hkdf_eh_tseh,
                     info=None).derive(shared_secret_sh_tseh)

        ck_hkdf_eh_st_kauth = HKDF(algorithm=hashes.SHA256(),
                        length=64,
                        salt=ck_hkdf_sh_tseh,
                        info=None).derive(shared_secret_eh_st)

        ck_hkdf_cmdres = ck_hkdf_eh_st_kauth[:32]
        kauth = ck_hkdf_eh_st_kauth[32:]

        hkdf_cmdres = HKDF(algorithm=hashes.SHA256(),
                        length=64,
                        salt=ck_hkdf_cmdres,
                        info=None).derive(b'')

        kcmd = hkdf_cmdres[:32]
        kres = hkdf_cmdres[32:]

        print("HKDF EH TSEH: {}".format(ck_hkdf_eh_tseh.hex()))
        print("HKDF SH TSEH: {}".format(ck_hkdf_sh_tseh.hex()))
        print("HKDF EH ST")
        print("  CMDRES: {}".format(ck_hkdf_cmdres.hex()))
        print("  KAUTH: {}".format(kauth.hex()))
        print("HKDF CMDRES")
        print("  KCMD: {}".format(kcmd.hex()))
        print("  KRES: {}".format(kres.hex()))

        aesgcm = AESGCM(kauth)
        ciphertext_with_tag = aesgcm.encrypt(nonce=b'\x00'*12, data=b'', associated_data=sha256hash.digest())

        tag = ciphertext_with_tag[-16:]
        ciphertext = ciphertext_with_tag[:-16]

        print("Ciphertext:", ciphertext)
        print("THAuth", tag.hex())

        print("THAuth == TSAuth: {}".format(tag == tsauth))

        # Clear hanshake data
        ck_hkdf_sh_tseh = None
        ck_hkdf_eh_tseh = None
        ck_hkdf_eh_st_kauth = None
        ck_hkdf_cmdres = None
        kauth = None

        encrypt_key = AESGCM(kcmd)
        decrypt_key = AESGCM(kres)

        self._secure_session = [ encrypt_key, decrypt_key ]

        return (kcmd, kres)


    def get_log(self):
        log = b''
        while True:
            part = self._l2_get_log()
            if not part:
                break

            log += part

        return log.decode("utf-8")


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


    def _random(self, length):
        raise NotImplementedError("Not implemented")

    def _get_ephemeral_keypair(self):
        raise NotImplementedError("Not implemented")
