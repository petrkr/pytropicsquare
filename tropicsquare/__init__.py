# by Petr Kracik (c) 2025

__version__ = "0.0.1"
__license__ = "MIT"


from tropicsquare.crc import CRC
from tropicsquare.constants import *
from tropicsquare.constants.chip_status import *
from tropicsquare.constants.get_info_req import *
from tropicsquare.constants.rsp_status import RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK, RSP_STATUS_REQ_CONT, RSP_STATUS_RES_CONT
from tropicsquare.constants.cmd_result import *
from tropicsquare.exceptions import *

from hashlib import sha256

from time import sleep

class TropicSquare:
    def __init__(self):
        self._secure_session = None
        self._certificate = None


    def _l2_get_response(self):
        chip_status = CHIP_STATUS_NOT_READY

        for _ in range(MAX_RETRIES):
            data = bytearray()
            data.extend(bytes(REQ_ID_GET_RESPONSE))

            self._spi_cs(0)
            self._spi_write_readinto(data, data)
            chip_status = data[0]

            if chip_status in [CHIP_STATUS_NOT_READY, CHIP_STATUS_BUSY]:
                self._spi_cs(1)
                sleep(0.025)
                continue

            if chip_status & CHIP_STATUS_ALARM:
                self._spi_cs(1)
                raise TropicSquareError("Chip is in alarm")

            response = self._spi.read(2)

            response_status = response[0]
            response_length = response[1]

            # If response status is 0xFF, it means that the chip is busy
            if response_status == 0xFF:
                sleep(0.025)
                continue

            if response_length > 0:
                data = self._spi.read(response_length)
            else:
                data = None

            calccrc = CRC.crc16(response + (data or b''))
            respcrc = self._spi.read(2)

            self._spi_cs(1)

            if response_status not in [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK, RSP_STATUS_RES_CONT, RSP_STATUS_REQ_CONT]:
                raise TropicSquareError("Response status is not OK (status: {})".format(hex(response_status)))

            if respcrc != calccrc:
                raise TropicSquareCRCError("CRC mismatch ({}<!=>{})".format(calccrc.hex(), respcrc.hex()))

            if response_status == RSP_STATUS_RES_CONT:
                data += self._l2_get_response()

            return data


        raise TropicSquareError("Chip is busy")


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

        return self._l2_get_response()


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

        data = self._l2_get_response()

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

        return self._l2_get_response()


    def _l2_encrypted_command(self, command_size, command_ciphertext, command_tag):
        def _chunk_data(data, chunk_size=128):
            for i in range(0, len(data), chunk_size):
                yield (data[i:i+chunk_size])

        # L3 Data to chunk
        l3data = bytearray()
        l3data.extend(command_size.to_bytes(COMMAND_SIZE_LEN, "little"))
        l3data.extend(command_ciphertext)
        l3data.extend(command_tag)

        for chunk in _chunk_data(l3data):
            data = bytearray()
            data.extend(bytes(REQ_ID_ENCRYPTED_CMD_REQ))
            data.append(len(chunk))
            data.extend(chunk)
            data.extend(CRC.crc16(data))

            self._spi_cs(0)
            self._spi_write_readinto(data, data)
            self._spi_cs(1)

            chip_status = data[0]

            if chip_status != CHIP_STATUS_READY:
                raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

            # Get response
            self._l2_get_response()

        # GET final response
        data = self._l2_get_response()

        command_size = int.from_bytes(data[0:2], "little")
        command_ciphertext = data[2:-16]
        command_tag = data[-16:]

        if command_size != len(command_ciphertext):
            raise TropicSquareError("Command size mismatch")


        return (command_ciphertext, command_tag)


    def _l2_encrypted_session_abt(self):
        data = bytearray()
        data.extend(bytes(REQ_ID_ENCRYPTED_SESSION_ABT))
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        self._l2_get_response()
        return True


    def _l2_sleep_req(self, sleep_mode):
        if sleep_mode not in [SLEEP_MODE_SLEEP, SLEEP_MODE_DEEP_SLEEP]:
            raise ValueError("Invalid sleep mode")

        data = bytearray()
        data.extend(bytes(REQ_ID_SLEEP_REQ))
        data.append(sleep_mode)
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        self._l2_get_response()
        return True


    def _l2_startup_req(self, startup_id):
        if startup_id not in [STARTUP_REBOOT, STARTUP_MAINTENANCE_REBOOT]:
            raise ValueError("Invalid sleep mode")

        data = bytearray()
        data.extend(bytes(REQ_ID_STARTUP_REQ))
        data.append(startup_id)
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        self._l2_get_response()
        return True


    @property
    def certificate(self) -> bytes:
        """Get X509 certificate from the chip

        Returns:
            bytes: X509 certificate
        """
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
    def public_key(self) -> bytes:
        """Get public key from the X509 certificate

        In case certificate is not loaded before, it will load also certificate

        Returns:
            bytes: Public key
        """
        if self._certificate is None:
            cert = self.certificate
        else :
            cert = self._certificate

        # Find signature for X25519 public key
        # 0x65, 0x6e, 0x03 and 0x21
        for i in range(len(cert)):
            if cert[i] == 0x65:
                if cert[i+1] == 0x6e and \
                    cert[i+2] == 0x03 and \
                    cert[i+3] == 0x21:
                    # Found it
                    # Plus 5 bytes to skip the signature
                    return cert[i+5:i+5+32]

        return None


    @property
    def chipid(self) -> bytes:
        return self._l2_get_info_req(GET_INFO_CHIPID)


    @property
    def riscv_fw_version(self) -> tuple:
        """Get RISCV firmware version

        Returns:
            tuple: Firmware version (major, minor, patch, release)
        """
        data = self._l2_get_info_req(GET_INFO_RISCV_FW_VERSION)
        return (data[3], data[2], data[1], data[0])


    @property
    def spect_fw_version(self) -> tuple:
        """Get SPECT firmware version

        Returns:
            tuple: Firmware version (major, minor, patch, release)
        """
        data = self._l2_get_info_req(GET_INFO_SPECT_FW_VERSION)
        return (data[3], data[2], data[1], data[0])


    @property
    def fw_bank(self):
        return self._l2_get_info_req(GET_INFO_FW_BANK)


    def start_secure_session(self, pkey_index : int, shpriv : bytes, shpub : bytes) -> bool:
        """Initialize secure session for L3 commands

        Args:
            phkey_index (int): Pairing key index
            shpriv (bytes): Pairing private key
            shpub (bytes): Pairing public key

        Returns:
            bool: True if secure session was established

        Raises:
            TropicSquareError: If secure session handshake failed
        """
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


    def abort_secure_session(self) -> bool:
        """Abort secure session

        Returns:
            bool: True if secure session was aborted
        """
        if self._l2_encrypted_session_abt():
            self._secure_session = None
            return True

        return False


    def get_log(self) -> str:
        """Get log from the RISC Firmware

        Returns:
            str: Log message
        """
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

    def ping(self, data : bytes) -> bytes:
        """Returns data back

        Args:
            data (bytes): Data to send

        Returns:
            bytes: Data from input
        """
        request_data = bytearray()
        request_data.append(CMD_ID_PING)
        request_data.extend(data)

        result = self._call_command(request_data)

        return result


    def get_random(self, nbytes : int) -> bytes:
        """Get random bytes

        Args:
            nbytes (int): Number of bytes to generate

        Returns:
            bytes: Random bytes
        """
        request_data = bytearray()
        request_data.append(CMD_ID_RANDOM_VALUE)
        request_data.extend(nbytes.to_bytes(1))

        result = self._call_command(request_data)

        return result[3:]


    def get_serial_code(self):
        request_data = bytearray()
        request_data.append(CMD_ID_SERIAL_CODE_GET)

        result = self._call_command(request_data)

        return result


    def r_config_read(self, address):
        request_data = bytearray()
        request_data.append(CMD_ID_R_CFG_READ)
        request_data.extend(address.to_bytes(CFG_ADDRESS_SIZE, "little"))

        result = self._call_command(request_data)

        return result[3:]


    def i_config_read(self, address):
        request_data = bytearray()
        request_data.append(CMD_ID_I_CFG_READ)
        request_data.extend(address.to_bytes(CFG_ADDRESS_SIZE, "little"))

        result = self._call_command(request_data)

        return result[3:]


    def mem_data_read(self, slot : int) -> bytes:
        """Read data from memory slot

        Args:
            slot (int): Memory slot

        Returns:
            bytes: Data from memory slot
        """
        request_data = bytearray()
        request_data.append(CMD_ID_R_MEMDATA_READ)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        result = self._call_command(request_data)

        return result[3:]


    def mem_data_write(self, data : bytes, slot : int) -> bool:
        """Write data to memory slot

        Args:
            data (bytes): Data to write (Maximum 444 bytes)
            slot (int): Memory slot

        Returns:
            bool: True if data was written

        Raises:
            ValueError: If data size is larger than 444
        """
        if len(data) > MEM_DATA_MAX_SIZE:
            raise ValueError("Data size is larger than MEM_DATA_MAX_SIZE")

        request_data = bytearray()
        request_data.append(CMD_ID_R_MEMDATA_WRITE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.extend(b'M') # Padding dummy data
        request_data.extend(data)

        self._call_command(request_data)

        return True


    def mem_data_erase(self, slot : int) -> bool:
        """Erase memory slot

        Args:
            slot (int): Memory slot

        Returns:
            bool: True if data was erased
        """
        request_data = bytearray()
        request_data.append(CMD_ID_R_MEMDATA_ERASE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        self._call_command(request_data)

        return True


    def ecc_key_generate(self, slot : int, curve : int) -> bool:
        """Generate ECC key

        Args:
            slot (int): Slot for key
            curve (int): Curve (ECC_CURVE_P256 or ECC_CURVE_ED25519)

        Returns:
            bool: True if key was generated

        Raises:
            ValueError: If slot is larger than ECC_MAX_KEYS or curve is invalid
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        if curve not in [ECC_CURVE_P256, ECC_CURVE_ED25519]:
            raise ValueError("Invalid curve")


        request_data = bytearray()
        request_data.append(CMD_ID_ECC_KEY_GENERATE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.append(curve)

        self._call_command(request_data)

        return True


    def ecc_key_store(self, slot : int, curve : int, key : bytes) -> bytes:
        """Store own ECC key

        Args:
            slot (int): Slot for key
            curve (int): Curve (ECC_CURVE_P256 or ECC_CURVE_ED25519)
            key (bytes): Private key

        Returns:
            bool: True if key was stored

        Raises:
            ValueError: If slot is larger than ECC_MAX_KEYS or curve is invalid
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        if curve not in [ECC_CURVE_P256, ECC_CURVE_ED25519]:
            raise ValueError("Invalid curve")

        request_data = bytearray()
        request_data.append(CMD_ID_ECC_KEY_STORE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.append(curve)
        request_data.extend(b'\x00'*12) # Padding dummy data (maybe do random?)
        request_data.extend(key)

        self._call_command(request_data)

        return True


    def ecc_key_read(self, slot : int) -> tuple:
        """Read ECC key

        Args:
            slot (int): Slot for key

        Returns:
            tuple: Curve, origin, public key

        Raises:
            ValueError: If slot is larger than ECC_MAX_KEYS
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        request_data = bytearray()
        request_data.append(CMD_ID_ECC_KEY_READ)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        result = self._call_command(request_data)

        curve = result[0]
        origin = result[1]
        pubkey = result[15:]

        return curve, origin, pubkey


    def ecc_key_erase(self, slot : int) -> bool:
        """Erase ECC key

        Args:
            slot (int): Slot for key

        Returns:
            bool: True if key was erased

        Raises:
            ValueError: If slot is larger than ECC_MAX_KEYS
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        request_data = bytearray()
        request_data.append(CMD_ID_ECC_KEY_ERASE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        self._call_command(request_data)

        return True


    def ecdsa_sign(self, slot : int, hash : bytes) -> tuple:
        """Sign hash with ECC key

        Args:
            slot (int): Slot with ECC key (ECC_CURVE_P256)
            hash (bytes): Hash to sign

        Returns:
            tuple: R and S values of the signature
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        request_data = bytearray()
        request_data.append(CMD_ID_ECDSA_SIGN)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.extend(b'\x00'*13) # Padding dummy data (maybe do random?)
        request_data.extend(hash)

        result = self._call_command(request_data)

        sign_r = result[15:47]
        sign_s = result[47:]

        return sign_r, sign_s


    def eddsa_sign(self, slot : int, message : bytes) -> tuple:
        """Sign message with ECC key

        Args:
            slot (int): Slot with ECC key (ECC_CURVE_ED25519)
            message (bytes): Message

        Returns:
            tuple: R and S values of the signature
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        request_data = bytearray()
        request_data.append(CMD_ID_EDDSA_SIGN)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.extend(b'\x00'*13) # Padding dummy data (maybe do random?)
        request_data.extend(message)

        result = self._call_command(request_data)

        sign_r = result[15:47]
        sign_s = result[47:]

        return sign_r, sign_s


    def mcounter_init(self, index : int, value : int) -> bool:
        """Initialize monotonic counter

        Args:
            index (int): Counter index
            value (int): Initial value

        Returns:
            bool: True if counter was initialized
        """
        if index > MCOUNTER_MAX:
            raise ValueError("Index is larger than MCOUNTER_MAX")

        request_data = bytearray()
        request_data.append(CMD_ID_MCOUNTER_INIT)
        request_data.extend(index.to_bytes(2, "little"))
        request_data.extend(b'A') # Padding dummy data
        request_data.extend(value.to_bytes(4, "little"))

        self._call_command(request_data)

        return True


    def mcounter_update(self, index : int) -> bool:
        """Decrement monotonic counter

        Args:
            index (int): Counter index

        Returns:
            bool: True if counter was updated
        """
        if index > MCOUNTER_MAX:
            raise ValueError("Index is larger than MCOUNTER_MAX")

        request_data = bytearray()
        request_data.append(CMD_ID_MCOUNTER_UPDATE)
        request_data.extend(index.to_bytes(2, "little"))

        self._call_command(request_data)

        return True


    def mcounter_get(self, index : int) -> int:
        """Get monotonic counter value

        Args:
            index (int): Counter index

        Returns:
            int: Counter value
        """
        if index > MCOUNTER_MAX:
            raise ValueError("Index is larger than MCOUNTER_MAX")

        request_data = bytearray()
        request_data.append(CMD_ID_MCOUNTER_GET)
        request_data.extend(index.to_bytes(2, "little"))

        result = self._call_command(request_data)

        return int.from_bytes(result[3:], "little")


    def mac_and_destroy(self, slot, data):
        if slot > MAC_AND_DESTROY_MAX:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        request_data = bytearray()
        request_data.append(CMD_ID_MAC_AND_DESTROY)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.extend(b'M') # Padding dummy data
        request_data.extend(data)

        result = self._call_command(request_data)

        return result[3:]


    def _call_command(self, data):
        if self._secure_session is None:
            raise TropicSquareNoSession("Secure session not started")

        nonce = self._secure_session[2].to_bytes(12, "little")

        enc = self._secure_session[0].encrypt(nonce=nonce, data=data, associated_data=b'')
        ciphertext = enc[:-16]
        tag = enc[-16:]

        result_cipher, result_tag = self._l2_encrypted_command(len(ciphertext), ciphertext, tag)
        decrypted = self._secure_session[1].decrypt(nonce=nonce, data=result_cipher+result_tag, associated_data=b'')

        self._secure_session[2] += 1

        if decrypted[0] != CMD_RESULT_OK:
            raise TropicSquareError("Command failed with result: {}".format(hex(decrypted[0])))

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
