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
from tropicsquare.transports import L1Transport
from tropicsquare.constants.l2 import *
from tropicsquare.constants.get_info_req import GET_INFO_DATA_CHUNK_0_127
from tropicsquare.exceptions import TropicSquareResponseError


class L2Protocol:
    """L2 protocol layer implementation.

        Provides low-level chip communication primitives for the TROPIC01
        secure element. This class handles SPI communication, framing,
        CRC validation, and chip state management.
    """

    def __init__(self, transport: L1Transport) -> None:
        """Initialize L2 protocol layer.

            :param transport: Transport instance
        """
        self._transport = transport


    def get_info_req(self, object_id: int, req_data_chunk: int = GET_INFO_DATA_CHUNK_0_127) -> bytes:
        """Request information object from chip.

            Sends GET_INFO request to retrieve chip information like certificate,
            chip ID, firmware version, etc.

            :param object_id: Information object type to retrieve
            :param req_data_chunk: Data chunk selector (for objects > 128 bytes)

            :returns: Raw information data
            :rtype: bytes

            :raises TropicSquareError: If chip status is not ready
        """
        payload = bytes([object_id, req_data_chunk])
        return self._send_and_get_response(REQ_ID_GET_INFO_REQ, payload)


    def handshake_req(self, ehpub: bytes, p_keyslot: int) -> tuple:
        """Perform secure session handshake.

            Sends ephemeral public key to chip and receives chip's ephemeral
            public key and authentication tag.

            :param ehpub: Ephemeral public key (32 bytes)
            :param p_keyslot: Pairing key slot index (0-3)

            :returns: (chip_ephemeral_pubkey, chip_auth_tag)
            :rtype: tuple

            :raises TropicSquareError: If chip status is not ready
        """
        payload = ehpub + bytes([p_keyslot])
        data = self._send_and_get_response(REQ_ID_HANDSHARE_REQ, payload)

        tsehpub = data[0:32]
        tsauth = data[32:48]

        return (tsehpub, tsauth)


    def get_log(self) -> bytes:
        """Retrieve firmware logs from chip.

            :returns: Raw log data
            :rtype: bytes

            :raises TropicSquareError: If chip status is not ready
        """
        return self._send_and_get_response(REQ_ID_GET_LOG_REQ)


    def encrypted_command(self, command_size: int, command_ciphertext: bytes, command_tag: bytes) -> tuple:
        """Send encrypted L3 command to chip.

            Handles chunking of large commands (> 128 bytes) and sends them
            to the chip. Returns encrypted response.

            :param command_size: Size of command ciphertext
            :param command_ciphertext: Encrypted command data
            :param command_tag: AES-GCM authentication tag (16 bytes)

            :returns: (response_ciphertext, response_tag)
            :rtype: tuple

            :raises TropicSquareError: If chip status is not ready
            :raises TropicSquareResponseError: If response size mismatch
        """
        def _chunk_data(data, chunk_size=128):
            for i in range(0, len(data), chunk_size):
                yield (data[i:i+chunk_size])

        # L3 Data to chunk
        l3data = bytearray()
        l3data.extend(command_size.to_bytes(COMMAND_SIZE_LEN, "little"))
        l3data.extend(command_ciphertext)
        l3data.extend(command_tag)

        # Send all chunks
        for chunk in _chunk_data(l3data):
            payload = bytes([len(chunk)]) + chunk
            request = self._build_request(REQ_ID_ENCRYPTED_CMD_REQ, payload)
            self._transport.send_request(request)
            # Get ACK response for this chunk
            self._transport.get_response()

        # Get final response
        data = self._transport.get_response()

        command_size = int.from_bytes(data[0:2], "little")
        command_ciphertext = data[2:-16]
        command_tag = data[-16:]

        if command_size != len(command_ciphertext):
            raise TropicSquareResponseError("Command size mismatch in response")

        return (command_ciphertext, command_tag)


    def encrypted_session_abt(self) -> bool:
        """Abort encrypted session.

            Terminates the current secure session with the chip.

            :returns: True on success
            :rtype: bool

            :raises TropicSquareError: If chip status is not ready
        """
        self._send_and_get_response(REQ_ID_ENCRYPTED_SESSION_ABT)
        return True


    def sleep_req(self, sleep_mode: int) -> bool:
        """Put chip to sleep.

            :param sleep_mode: Sleep mode (SLEEP_MODE_SLEEP or SLEEP_MODE_DEEP_SLEEP)

            :returns: True on success
            :rtype: bool

            :raises ValueError: If invalid sleep mode
            :raises TropicSquareError: If chip status is not ready
        """

        payload = bytes([sleep_mode])
        self._send_and_get_response(REQ_ID_SLEEP_REQ, payload)
        return True


    def startup_req(self, startup_id: int) -> bool:
        """Startup/reboot chip.

            :param startup_id: Startup mode (STARTUP_REBOOT or STARTUP_MAINTENANCE_REBOOT)

            :returns: True on success
            :rtype: bool

            :raises ValueError: If invalid startup mode
            :raises TropicSquareError: If chip status is not ready
        """

        payload = bytes([startup_id])
        self._send_and_get_response(REQ_ID_STARTUP_REQ, payload)
        return True


    # === Private helper methods for reducing code duplication ===

    def _build_request(self, req_id, payload=b''):
        """Build request frame with CRC.

            :param req_id: Request ID bytes (e.g., REQ_ID_GET_INFO_REQ)
            :param payload: Optional payload bytes

            :returns: Complete request with CRC
            :rtype: bytearray
        """
        data = bytearray()
        data.extend(bytes(req_id))
        data.extend(payload)
        data.extend(CRC.crc16(data))
        return data


    def _send_and_get_response(self, req_id, payload=b''):
        """Build request, send it, check status, and get response.

        Convenience method that combines common pattern of:
        1. Build request with CRC
        2. Send via transport
        3. Get response

            :param req_id: Request ID bytes
            :param payload: Optional payload bytes

            :returns: Response data from chip
            :rtype: bytes

            :raises TropicSquareError: If chip is not ready
        """
        request = self._build_request(req_id, payload)
        self._transport.send_request(request)
        return self._transport.get_response()
