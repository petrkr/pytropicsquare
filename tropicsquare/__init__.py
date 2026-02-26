# by Petr Kracik (c) 2026

__version__ = "0.1.0"
__license__ = "MIT"


from tropicsquare.constants.l2 import SLEEP_MODE_DEEP_SLEEP, SLEEP_MODE_SLEEP, STARTUP_REBOOT, STARTUP_MAINTENANCE_REBOOT
from tropicsquare.l2_protocol import L2Protocol
from tropicsquare.transports import L1Transport
from tropicsquare.constants import *
from tropicsquare.constants.ecc import ECC_MAX_KEYS, ECC_CURVE_P256, ECC_CURVE_ED25519
from tropicsquare.constants.get_info_req import *
from tropicsquare.exceptions import *
from tropicsquare.error_mapping import raise_for_cmd_result
from tropicsquare.chip_id import ChipId
from tropicsquare.config import parse_config
from tropicsquare.config.base import BaseConfig
from tropicsquare.ecc import EccKeyInfo
from tropicsquare.ecc.signature import EcdsaSignature, EddsaSignature

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


    def __init__(self, transport: L1Transport) -> None:
        """Initialize TropicSquare base class.

            :param transport: L1Transport instance
        """
        self._secure_session = None
        self._certificate = None

        # Create L2 protocol layer with transport
        self._l2 = L2Protocol(transport)


    @property
    def certificate(self) -> bytes:
        """Get X509 certificate from the chip

            :returns: X509 certificate
            :rtype: bytes
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

            :returns: Public key
            :rtype: bytes
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

            :returns: Parsed chip ID object with all fields
            :rtype: ChipId
        """
        raw_data = self._l2.get_info_req(GET_INFO_CHIPID)
        return ChipId(raw_data)


    @property
    def riscv_fw_version(self) -> tuple:
        """Get RISCV firmware version

            :returns: Firmware version (major, minor, patch, release)
            :rtype: tuple
        """
        data = self._l2.get_info_req(GET_INFO_RISCV_FW_VERSION)
        return (data[3], data[2], data[1], data[0])


    @property
    def spect_fw_version(self) -> tuple:
        """Get SPECT firmware version

            :returns: Firmware version (major, minor, patch, release)
            :rtype: tuple
        """
        data = self._l2.get_info_req(GET_INFO_SPECT_FW_VERSION)
        return (data[3], data[2], data[1], data[0])


    @property
    def fw_bank(self) -> bytes:
        """Get firmware bank information.

            :returns: Firmware bank data
            :rtype: bytes
        """
        return self._l2.get_info_req(GET_INFO_FW_BANK)


    def start_secure_session(self, pkey_index : int, shpriv : bytes, shpub : bytes) -> bool:
        """Initialize secure session for L3 commands

            :param phkey_index: Pairing key index
            :param shpriv: Pairing private key
            :param shpub: Pairing public key

            :returns: True if secure session was established
            :rtype: bool

            :raises TropicSquareError: If secure session handshake failed
        """
        if not 0 <= pkey_index <= PAIRING_KEY_MAX:
            raise ValueError(
                f"Pairing key slot must be in range 0-{PAIRING_KEY_MAX}, got {pkey_index}"
            )

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

            :returns: True if secure session was aborted
            :rtype: bool
        """
        if self._l2.encrypted_session_abt():
            self._secure_session = None
            return True

        return False

    def reboot(self, mode: int) -> bool:
        """Startup/reboot chip

            :param mode: Startup mode (STARTUP_REBOOT or STARTUP_MAINTENANCE_REBOOT)

            :returns: True if startup request was sent
            :rtype: bool

            :raises ValueError: If invalid startup mode
            :raises TropicSquareError: If startup request failed
        """
        if mode not in [STARTUP_REBOOT, STARTUP_MAINTENANCE_REBOOT]:
            raise ValueError("Invalid startup mode")

        return self._l2.startup_req(mode)


    def sleep(self, mode: int) -> bool:
        """Put chip to sleep

            :param mode: Sleep mode (SLEEP_MODE_SLEEP or SLEEP_MODE_DEEP_SLEEP)

            :returns: True if sleep request was sent
            :rtype: bool

            :raises ValueError: If invalid sleep mode
            :raises TropicSquareError: If sleep request failed
        """
        if mode not in [SLEEP_MODE_SLEEP, SLEEP_MODE_DEEP_SLEEP]:
            raise ValueError("Invalid sleep mode")

        return self._l2.sleep_req(mode)


    def get_log(self) -> str:
        """Get log from the RISC Firmware

            :returns: Log message
            :rtype: str
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

            :param data: Data to send

            :returns: Data from input
            :rtype: bytes
        """
        request_data = bytearray()
        request_data.append(CMD_ID_PING)
        request_data.extend(data)

        result = self._call_command(request_data)

        return result


    def get_random(self, nbytes : int) -> bytes:
        """Get random bytes

            :param nbytes: Number of bytes to generate

            :returns: Random bytes
            :rtype: bytes
        """
        request_data = bytearray()
        request_data.append(CMD_ID_RANDOM_VALUE)
        request_data.extend(nbytes.to_bytes(1, "little"))

        result = self._call_command(request_data)

        return result[3:]


    def r_config_read(self, address: int):
        """Read and parse R-CONFIG register.

            :param address: Register address (use CFG_* constants from tropicsquare.constants.config)

            :returns: Parsed config object (StartUpConfig, SensorsConfig, etc.)
            :rtype: BaseConfig

            Example::

                from tropicsquare.constants.config import CFG_START_UP

                config = ts.r_config_read(CFG_START_UP)
                print(config.mbist_dis)
        """
        data = self._config_read_raw(CMD_ID_R_CFG_READ, address)
        return parse_config(address, data)


    def i_config_read(self, address: int):
        """Read and parse I-CONFIG register.

            :param address: Register address (use CFG_* constants from tropicsquare.constants.config)

            :returns: Parsed config object (StartUpConfig, SensorsConfig, etc.)
            :rtype: BaseConfig

            Example::

                from tropicsquare.constants.config import CFG_START_UP

                config = ts.i_config_read(CFG_START_UP)
                print(config.mbist_dis)
        """
        data = self._config_read_raw(CMD_ID_I_CFG_READ, address)
        return parse_config(address, data)


    def r_config_write(self, address: int, value) -> bool:
        """Write single R-CONFIG register.

            :param address: Register address (use CFG_* constants from tropicsquare.constants.config)
            :param value: 32-bit register value or BaseConfig object

            :returns: True if write succeeded
            :rtype: bool
        """
        self._config_write_raw(CMD_ID_R_CFG_WRITE, address, value)
        return True


    def i_config_write(self, address: int, value) -> bool:
        """Write single I-CONFIG register.

            :param address: Register address (use CFG_* constants from tropicsquare.constants.config)
            :param value: 32-bit register value or BaseConfig object

            :returns: True if write succeeded
            :rtype: bool
        """
        self._config_write_raw(CMD_ID_I_CFG_WRITE, address, value)
        return True


    def r_config_erase(self) -> bool:
        """Erase whole R-CONFIG (sets all bits of all COs to 1).

            :returns: True if erase succeeded
            :rtype: bool
        """
        request_data = bytearray()
        request_data.append(CMD_ID_R_CFG_ERASE)
        self._call_command(request_data)
        return True


    def _config_read_raw(self, cmd_id: int, address: int) -> bytes:
        """Read raw 4-byte config value payload for a single CO."""
        self._validate_config_address(address)

        request_data = bytearray()
        request_data.append(cmd_id)
        request_data.extend(address.to_bytes(CFG_ADDRESS_SIZE, "little"))
        result = self._call_command(request_data)
        return result[3:]


    def _config_write_raw(self, cmd_id: int, address: int, value) -> None:
        """Write raw 4-byte config value payload for a single CO."""
        self._validate_config_address(address)
        value_bytes = self._config_value_to_bytes(value)

        request_data = bytearray()
        request_data.append(cmd_id)
        request_data.extend(address.to_bytes(CFG_ADDRESS_SIZE, "little"))
        request_data.extend(b'M')  # Padding dummy data
        request_data.extend(value_bytes)
        self._call_command(request_data)


    def _config_value_to_bytes(self, value) -> bytes:
        """Convert config value input to 4-byte wire format."""
        if isinstance(value, BaseConfig):
            return value.to_bytes()

        if not isinstance(value, int):
            raise TypeError("value must be int or BaseConfig")

        if not 0 <= value <= 0xFFFFFFFF:
            raise ValueError("Config value must be 32-bit unsigned integer")

        return value.to_bytes(4, "little")


    def _validate_config_address(self, address: int) -> None:
        """Validate 16-bit config CO address."""
        if not isinstance(address, int):
            raise TypeError("Config address must be integer")
        if not 0 <= address <= 0xFFFF:
            raise ValueError("Config address must be 16-bit (0x0000-0xFFFF)")


    def mem_data_read(self, slot : int) -> bytes:
        """Read data from memory slot

            :param slot: Memory slot

            :returns: Data from memory slot
            :rtype: bytes
        """
        request_data = bytearray()
        request_data.append(CMD_ID_R_MEMDATA_READ)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        result = self._call_command(request_data)

        return result[3:]


    def mem_data_write(self, data : bytes, slot : int) -> bool:
        """Write data to memory slot

            :param data: Data to write (Maximum 444 bytes)
            :param slot: Memory slot

            :returns: True if data was written
            :rtype: bool

            :raises ValueError: If data size is larger than 444
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

            :param slot: Memory slot

            :returns: True if data was erased
            :rtype: bool
        """
        request_data = bytearray()
        request_data.append(CMD_ID_R_MEMDATA_ERASE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        self._call_command(request_data)

        return True


    def ecc_key_generate(self, slot : int, curve : int) -> bool:
        """Generate ECC key

            :param slot: Slot for key
            :param curve: Curve (ECC_CURVE_P256 or ECC_CURVE_ED25519)

            :returns: True if key was generated
            :rtype: bool

            :raises ValueError: If slot is larger than ECC_MAX_KEYS or curve is invalid
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

            :param slot: Slot for key
            :param curve: Curve (ECC_CURVE_P256 or ECC_CURVE_ED25519)
            :param key: Private key

            :returns: True if key was stored
            :rtype: bool

            :raises ValueError: If slot is larger than ECC_MAX_KEYS or curve is invalid
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


    def ecc_key_read(self, slot : int) -> EccKeyInfo:
        """Read ECC key information from slot

            :param slot: Slot for key

            :returns: Key information with curve, origin, and public_key
            :rtype: EccKeyInfo

            :raises ValueError: If slot is larger than ECC_MAX_KEYS

            Example::

                key_info = ts.ecc_key_read(0)
                if key_info.curve == ECC_CURVE_ED25519:
                    print("Ed25519 key")
                print(key_info.public_key.hex())
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

        return EccKeyInfo(curve, origin, pubkey)


    def ecc_key_erase(self, slot : int) -> bool:
        """Erase ECC key

            :param slot: Slot for key

            :returns: True if key was erased
            :rtype: bool

            :raises ValueError: If slot is larger than ECC_MAX_KEYS
        """
        if slot > ECC_MAX_KEYS:
            raise ValueError("Slot is larger than ECC_MAX_KEYS")

        request_data = bytearray()
        request_data.append(CMD_ID_ECC_KEY_ERASE)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))

        self._call_command(request_data)

        return True


    def ecdsa_sign(self, slot : int, hash : bytes) -> EcdsaSignature:
        """Sign hash with ECDSA using P256 key

            :param slot: Slot with P256 ECC key
            :param hash: Hash to sign (32 bytes)

            :returns: ECDSA signature
            :rtype: EcdsaSignature

            :raises ValueError: If slot is larger than ECC_MAX_KEYS

            Example::

                import hashlib
                message_hash = hashlib.sha256(b"Hello").digest()
                signature = ts.ecdsa_sign(1, message_hash)
                print(signature.r.hex())
                print(signature.s.hex())
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

        return EcdsaSignature(sign_r, sign_s)


    def eddsa_sign(self, slot : int, message : bytes) -> EddsaSignature:
        """Sign message with EdDSA using Ed25519 key

            :param slot: Slot with Ed25519 ECC key
            :param message: Message to sign

            :returns: EdDSA signature
            :rtype: EddsaSignature

            Example::

                signature = ts.eddsa_sign(0, message)
                print(signature.r.hex())
                print(signature.s.hex())
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

        return EddsaSignature(sign_r, sign_s)


    def mcounter_init(self, index : int, value : int) -> bool:
        """Initialize monotonic counter

            :param index: Counter index
            :param value: Initial value

            :returns: True if counter was initialized
            :rtype: bool
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

            :param index: Counter index

            :returns: True if counter was updated
            :rtype: bool
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

            :param index: Counter index

            :returns: Counter value
            :rtype: int
        """
        if index > MCOUNTER_MAX:
            raise ValueError("Index is larger than MCOUNTER_MAX")

        request_data = bytearray()
        request_data.append(CMD_ID_MCOUNTER_GET)
        request_data.extend(index.to_bytes(2, "little"))

        result = self._call_command(request_data)

        return int.from_bytes(result[3:], "little")


    def mac_and_destroy(self, slot: int, data: bytes) -> bytes:
        """MAC and destroy operation for atomic PIN verification.

        This command executes atomic PIN verification using Keccak-based MAC.
        The operation reads a slot from the MAC-and-Destroy partition (128 slots, 0-127),
        performs MAC calculation, and destroys/erases the slot data.

        The MAC-and-Destroy partition is separate from User Data partition and
        uses Keccak engines with PUF-based per-chip unique keys (K_FXA, K_FXB).

        :param slot: Slot index in MAC-and-Destroy partition (0-127)
        :param data: Data to MAC (must be exactly 32 bytes)

        :returns: MAC result (32 bytes)

        :raises ValueError: If slot exceeds maximum (127) or data length is not 32 bytes
        :raises TropicSquareNoSession: If secure session is not established

        .. note::
           Requires active secure session via :meth:`start_secure_session`.

        .. seealso::
           TROPIC01 User API v1.1.2, Table 37: MAC_And_Destroy command specification

        Example::

            # Start secure session first
            ts.start_secure_session(
                FACTORY_PAIRING_KEY_INDEX,
                FACTORY_PAIRING_PRIVATE_KEY_PROD0,
                FACTORY_PAIRING_PUBLIC_KEY_PROD0
            )

            # Perform MAC and destroy on slot 0
            pin_data = b'my_32_byte_pin_data_here_000'  # Exactly 32 bytes
            mac_result = ts.mac_and_destroy(0, pin_data)
            print(f"MAC: {mac_result.hex()}")  # Returns 32-byte MAC
        """
        if slot > MAC_AND_DESTROY_MAX:
            raise ValueError(f"Slot {slot} exceeds maximum MAC_AND_DESTROY_MAX ({MAC_AND_DESTROY_MAX})")

        # Validate data length - must be exactly 32 bytes per API specification
        if len(data) != MAC_AND_DESTROY_DATA_SIZE:
            raise ValueError(
                f"Data must be exactly {MAC_AND_DESTROY_DATA_SIZE} bytes "
                f"(got {len(data)} bytes). See TROPIC01 User API Table 37."
            )

        request_data = bytearray()
        request_data.append(CMD_ID_MAC_AND_DESTROY)
        request_data.extend(slot.to_bytes(MEM_ADDRESS_SIZE, "little"))
        request_data.extend(b'M') # Padding dummy data
        request_data.extend(data)

        result = self._call_command(request_data)

        return result[3:]


    def pairing_key_read(self, slot: int) -> bytes:
        """Read pairing key information from slot.

            :param slot: Pairing key slot index (0-3)

            :returns: Pairing key information (32 bytes)
            :rtype: bytes

            :raises ValueError: If slot exceeds maximum (3)
        """
        if not 0 <= slot <= PAIRING_KEY_MAX:
            raise ValueError(
                f"Pairing key slot must be in range 0-{PAIRING_KEY_MAX}, got {slot}"
            )

        request_data = bytearray()
        request_data.append(CMD_ID_PAIRING_KEY_READ)
        request_data.extend(slot.to_bytes(PAIRING_ADDRESS_SIZE, "little"))
        result = self._call_command(request_data)

        return result[3:]


    def pairing_key_write(self, slot: int, key: bytes) -> bool:
        """Write pairing key information to slot.

            :param slot: Pairing key slot index (0-3)
            :param key: Pairing key data (32 bytes)

            :returns: True if write succeeded
            :rtype: bool

            :raises ValueError: If slot exceeds maximum (3) or key length is not 32 bytes
        """
        if not 0 <= slot <= PAIRING_KEY_MAX:
            raise ValueError(
                f"Pairing key slot must be in range 0-{PAIRING_KEY_MAX}, got {slot}"
            )

        if len(key) != PAIRING_KEY_SIZE:
            raise ValueError(f"Key must be exactly {PAIRING_KEY_SIZE} bytes")

        request_data = bytearray()
        request_data.append(CMD_ID_PAIRING_KEY_WRITE)
        request_data.extend(slot.to_bytes(PAIRING_ADDRESS_SIZE, "little"))
        request_data.extend(b'M') # Padding dummy data
        request_data.extend(key)

        result = self._call_command(request_data)

        return True


    def pairing_key_invalidate(self, slot: int) -> bool:
        """Invalidate pairing key in slot.

            :param slot: Pairing key slot index (0-3)

            :returns: True if successful
            :rtype: bool

            :raises ValueError: If slot exceeds maximum (3)
        """
        if not 0 <= slot <= PAIRING_KEY_MAX:
            raise ValueError(
                f"Pairing key slot must be in range 0-{PAIRING_KEY_MAX}, got {slot}"
            )

        request_data = bytearray()
        request_data.append(CMD_ID_PAIRING_KEY_INVALIDATE)
        request_data.extend(slot.to_bytes(PAIRING_ADDRESS_SIZE, "little"))

        self._call_command(request_data)

        return True

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


    def _hkdf(self, salt, shared_secret, length=1):
        raise NotImplementedError("Not implemented")


    def _x25519_exchange(self, private_bytes, public_bytes):
        raise NotImplementedError("Not implemented")


    def _aesgcm(self, key):
        raise NotImplementedError("Not implemented")
