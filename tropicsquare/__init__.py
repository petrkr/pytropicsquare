# by Petr Kracik (c) 2025

__version__ = "0.0.1"
__license__ = "MIT"


from tropicsquare.l2_protocol import L2Protocol
from tropicsquare.constants import *
from tropicsquare.constants.get_info_req import *
from tropicsquare.exceptions import *
from tropicsquare.error_mapping import raise_for_cmd_result
from tropicsquare.chip_id import ChipId

from hashlib import sha256


class TropicSquare:
    def __new__(cls, *args, **kwargs):
        """Factory method that returns platform-specific implementation.

        When instantiating TropicSquare directly, automatically returns
        either TropicSquareCPython or TropicSquareMicroPython based on
        the detected platform.

        This allows users to write platform-agnostic code:
            from tropicsquare import TropicSquare
            ts = TropicSquare(spi, cs)
        """
        if cls is not TropicSquare:
            return super().__new__(cls)

        # Only do platform detection when instantiating base class directly
        import sys
        if sys.implementation.name == 'micropython':
            from tropicsquare.ports.micropython import TropicSquareMicroPython
            return TropicSquareMicroPython(*args, **kwargs)

        if sys.implementation.name == 'cpython':
            from tropicsquare.ports.cpython import TropicSquareCPython
            return TropicSquareCPython(*args, **kwargs)

        raise TropicSquareError("Unsupported Python implementation: {}".format(sys.implementation.name))


    def __init__(self, spi=None, cs=None):
        """Initialize TropicSquare base class.

        Args:
            spi: SPI interface object (optional for direct base class use)
            cs: Chip select pin object (optional for direct base class use)

        Note:
            Platform-specific subclasses should pass spi and cs to super().__init__()
        """
        self._spi = spi
        self._cs = cs
        self._secure_session = None
        self._certificate = None

        # Create L2 protocol layer if SPI is provided
        if spi is not None and cs is not None:
            self._l2 = L2Protocol(spi, cs)


    @property
    def certificate(self) -> bytes:
        """Get X509 certificate from the chip

        Returns:
            bytes: X509 certificate
        """
        if self._certificate:
            return self._certificate

        data = self._l2.get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_0_127)
        data += self._l2.get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_128_255)
        data += self._l2.get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_256_383)
        data += self._l2.get_info_req(GET_INFO_X509_CERT, GET_INFO_DATA_CHUNK_384_511)

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
    def chipid(self) -> ChipId:
        """Get parsed chip ID structure

        Returns:
            ChipId: Parsed chip ID object with all fields
        """
        raw_data = self._l2.get_info_req(GET_INFO_CHIPID)
        return ChipId(raw_data)


    @property
    def riscv_fw_version(self) -> tuple:
        """Get RISCV firmware version

        Returns:
            tuple: Firmware version (major, minor, patch, release)
        """
        data = self._l2.get_info_req(GET_INFO_RISCV_FW_VERSION)
        return (data[3], data[2], data[1], data[0])


    @property
    def spect_fw_version(self) -> tuple:
        """Get SPECT firmware version

        Returns:
            tuple: Firmware version (major, minor, patch, release)
        """
        data = self._l2.get_info_req(GET_INFO_SPECT_FW_VERSION)
        return (data[3], data[2], data[1], data[0])


    @property
    def fw_bank(self):
        return self._l2.get_info_req(GET_INFO_FW_BANK)


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
        tsehpub, tsauth = self._l2.handshake_req(ehpub, pkey_index)

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
        sha256hash.update(pkey_index.to_bytes(1, "little"))

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
            raise TropicSquareHandshakeError("Authentication tag mismatch - handshake failed")

        encrypt_key = self._aesgcm(kcmd)
        decrypt_key = self._aesgcm(kres)

        self._secure_session = [ encrypt_key, decrypt_key, 0 ]

        return True


    def abort_secure_session(self) -> bool:
        """Abort secure session

        Returns:
            bool: True if secure session was aborted
        """
        if self._l2.encrypted_session_abt():
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
            part = self._l2.get_log()
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
        request_data.extend(nbytes.to_bytes(1, "little"))

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
            raise ValueError(f"Data size ({len(data)} bytes) exceeds maximum allowed size ({MEM_DATA_MAX_SIZE} bytes)")

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

        result_cipher, result_tag = self._l2.encrypted_command(len(ciphertext), ciphertext, tag)
        decrypted = self._secure_session[1].decrypt(nonce=nonce, data=result_cipher+result_tag, associated_data=b'')

        self._secure_session[2] += 1

        raise_for_cmd_result(decrypted[0])

        return decrypted[1:]


    def _get_ephemeral_keypair(self):
        raise NotImplementedError("Not implemented")


    def _hkdf(self, salt, shared_secret, length):
        raise NotImplementedError("Not implemented")


    def _x25519_exchange(self, private_bytes, public_bytes):
        raise NotImplementedError("Not implemented")


    def _aesgcm(self, key):
        raise NotImplementedError("Not implemented")
