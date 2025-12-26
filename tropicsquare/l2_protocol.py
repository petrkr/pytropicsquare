"""L2 Protocol Layer for TROPIC01 Secure Element

This module implements the L2 (Link Layer) protocol for communication
with the TROPIC01 chip. It handles low-level SPI communication, CRC
validation, retry logic, and message framing.

The L2 layer is responsible for:
- SPI bus communication and chip select management
- Request/response framing and CRC validation
- Chip status monitoring and retry logic
- Encrypted command transmission
- Session handshake protocol

The L2 layer does NOT handle:
- Cryptographic operations (delegated to parent)
- Command parsing/building (done by L3 layer)
- Session state management (done by TropicSquare)
"""

from tropicsquare.crc import CRC
from tropicsquare.constants.l2 import *
from tropicsquare.constants.chip_status import *
from tropicsquare.constants.rsp_status import RSP_STATUS_RES_CONT
from tropicsquare.constants.get_info_req import GET_INFO_DATA_CHUNK_0_127
from tropicsquare.exceptions import *
from tropicsquare.error_mapping import raise_for_response_status

from time import sleep


class L2Protocol:
    """L2 protocol layer implementation.

    Provides low-level chip communication primitives for the TROPIC01
    secure element. This class handles SPI communication, framing,
    CRC validation, and chip state management.
    """

    def __init__(self, spi, cs):
        """Initialize L2 protocol layer.

        Args:
            spi: SPI interface object (platform-specific)
            cs: Chip select pin object (platform-specific)
            parent: Parent TropicSquare instance (for crypto operations)
        """
        self._spi = spi
        self._cs = cs


    def get_response(self):
        """Get response from chip with automatic retry logic.

        Polls the chip for a response with automatic retry on busy status.
        Handles response fragmentation (CONT status) automatically.

        Returns:
            bytes: Response data from chip

        Raises:
            TropicSquareAlarmError: If chip is in alarm state
            TropicSquareCRCError: If CRC validation fails
            TropicSquareTimeoutError: If chip remains busy after max retries
            TropicSquareError: On other communication errors
        """
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
                raise TropicSquareAlarmError("Chip is in alarm state")

            response = self._spi_read(2)

            response_status = response[0]
            response_length = response[1]

            # If response status is 0xFF, it means that the chip is busy
            if response_status == 0xFF:
                sleep(0.025)
                continue

            if response_length > 0:
                data = self._spi_read(response_length)
            else:
                data = None

            calccrc = CRC.crc16(response + (data or b''))
            respcrc = self._spi_read(2)

            self._spi_cs(1)

            raise_for_response_status(response_status)

            if respcrc != calccrc:
                raise TropicSquareCRCError("CRC mismatch ({}<!=>{})".format(calccrc.hex(), respcrc.hex()))

            if response_status == RSP_STATUS_RES_CONT:
                data += self.get_response()

            return data

        raise TropicSquareTimeoutError("Chip communication timeout - chip remains busy")


    def get_info_req(self, object_id, req_data_chunk=GET_INFO_DATA_CHUNK_0_127):
        """Request information object from chip.

        Sends GET_INFO request to retrieve chip information like certificate,
        chip ID, firmware version, etc.

        Args:
            object_id: Information object type to retrieve
            req_data_chunk: Data chunk selector (for objects > 128 bytes)

        Returns:
            bytes: Raw information data

        Raises:
            TropicSquareError: If chip status is not ready
        """
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

        return self.get_response()


    def handshake_req(self, ehpub, p_keyslot):
        """Perform secure session handshake.

        Sends ephemeral public key to chip and receives chip's ephemeral
        public key and authentication tag.

        Args:
            ehpub: Ephemeral public key (32 bytes)
            p_keyslot: Pairing key slot index (0-3)

        Returns:
            tuple: (chip_ephemeral_pubkey, chip_auth_tag)

        Raises:
            TropicSquareError: If chip status is not ready
        """
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

        data = self.get_response()

        tsehpub = data[0:32]
        tsauth = data[32:48]

        return (tsehpub, tsauth)


    def get_log(self):
        """Retrieve firmware logs from chip.

        Returns:
            bytes: Raw log data

        Raises:
            TropicSquareError: If chip status is not ready
        """
        data = bytearray()
        data.extend(bytes(REQ_ID_GET_LOG_REQ))
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        return self.get_response()


    def encrypted_command(self, command_size, command_ciphertext, command_tag):
        """Send encrypted L3 command to chip.

        Handles chunking of large commands (> 128 bytes) and sends them
        to the chip. Returns encrypted response.

        Args:
            command_size: Size of command ciphertext
            command_ciphertext: Encrypted command data
            command_tag: AES-GCM authentication tag (16 bytes)

        Returns:
            tuple: (response_ciphertext, response_tag)

        Raises:
            TropicSquareError: If chip status is not ready
            TropicSquareResponseError: If response size mismatch
        """
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
            self.get_response()

        # GET final response
        data = self.get_response()

        command_size = int.from_bytes(data[0:2], "little")
        command_ciphertext = data[2:-16]
        command_tag = data[-16:]

        if command_size != len(command_ciphertext):
            raise TropicSquareResponseError("Command size mismatch in response")

        return (command_ciphertext, command_tag)


    def encrypted_session_abt(self):
        """Abort encrypted session.

        Terminates the current secure session with the chip.

        Returns:
            bool: True on success

        Raises:
            TropicSquareError: If chip status is not ready
        """
        data = bytearray()
        data.extend(bytes(REQ_ID_ENCRYPTED_SESSION_ABT))
        data.extend(CRC.crc16(data))

        self._spi_cs(0)
        self._spi_write_readinto(data, data)
        self._spi_cs(1)

        chip_status = data[0]

        if chip_status != CHIP_STATUS_READY:
            raise TropicSquareError("Chip status is not ready (status: {})".format(hex(chip_status)))

        self.get_response()
        return True


    def sleep_req(self, sleep_mode):
        """Put chip to sleep.

        Args:
            sleep_mode: Sleep mode (SLEEP_MODE_SLEEP or SLEEP_MODE_DEEP_SLEEP)

        Returns:
            bool: True on success

        Raises:
            ValueError: If invalid sleep mode
            TropicSquareError: If chip status is not ready
        """
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

        self.get_response()
        return True


    def startup_req(self, startup_id):
        """Startup/reboot chip.

        Args:
            startup_id: Startup mode (STARTUP_REBOOT or STARTUP_MAINTENANCE_REBOOT)

        Returns:
            bool: True on success

        Raises:
            ValueError: If invalid startup mode
            TropicSquareError: If chip status is not ready
        """
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

        self.get_response()
        return True


    # === Private SPI wrapper methods ===

    def _spi_cs(self, value):
        self._cs.value(value)


    def _spi_read(self, length):
        return self._spi.read(length)


    def _spi_write_readinto(self, tx_buffer, rx_buffer):
        self._spi.write_readinto(tx_buffer, rx_buffer)
