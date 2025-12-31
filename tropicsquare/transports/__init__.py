"""L1 Transport Layer for TROPIC01

This module provides the base class for L1 transport implementations.
"""

from time import sleep

from tropicsquare.constants.chip_status import CHIP_STATUS_NOT_READY, CHIP_STATUS_BUSY, CHIP_STATUS_ALARM
from tropicsquare.constants.l1 import REQ_ID_GET_RESPONSE, MAX_RETRIES
from tropicsquare.constants.rsp_status import RSP_STATUS_RES_CONT
from tropicsquare.exceptions import TropicSquareAlarmError, TropicSquareCRCError, TropicSquareTimeoutError
from tropicsquare.crc import CRC
from tropicsquare.error_mapping import raise_for_response_status


class L1Transport():
    """Base class for L1 transport layer.

    Platform-specific classes implement only abstract low-level methods.
    """

    def send_request(self, request_data: bytes) -> bytes:
        """Send request to chip and return response bytes.

        :param request_data: Complete request frame (with CRC)
        :type request_data: bytes
        :returns: Response bytes
        :rtype: bytes
        """

        self._cs_low()
        rx_data = self._transfer(request_data)
        self._cs_high()

        return rx_data


    def get_response(self) -> bytes:
        """Get response from chip with automatic retry logic.

        :returns: Response data from chip
        :rtype: bytes
        :raises TropicSquareAlarmError: If chip is in alarm state
        :raises TropicSquareCRCError: If CRC validation fails
        :raises TropicSquareTimeoutError: If chip remains busy after max retries
        :raises TropicSquareError: On other communication errors
        """

        chip_status = CHIP_STATUS_NOT_READY

        for _ in range(MAX_RETRIES):
            data = bytearray()
            data.extend(bytes(REQ_ID_GET_RESPONSE))

            self._cs_low()
            data[:] = self._transfer(data)
            chip_status = data[0]

            if chip_status in [CHIP_STATUS_NOT_READY, CHIP_STATUS_BUSY]:
                self._cs_high()
                sleep(0.025)
                continue

            if chip_status & CHIP_STATUS_ALARM:
                self._cs_high()
                raise TropicSquareAlarmError("Chip is in alarm state")

            response = self._read(2)

            response_status = response[0]
            response_length = response[1]

            if response_status == CHIP_STATUS_BUSY:
                self._cs_high()
                sleep(0.025)
                continue

            if response_length > 0:
                data = self._read(response_length)
            else:
                data = None

            calccrc = CRC.crc16(response + (data or b''))
            respcrc = self._read(2)

            self._cs_high()

            raise_for_response_status(response_status)

            if respcrc != calccrc:
                raise TropicSquareCRCError(
                    f"CRC mismatch ({calccrc.hex()}<!=>{respcrc.hex()})"
                )

            if response_status == RSP_STATUS_RES_CONT:
                data += self.get_response()

            return data

        raise TropicSquareTimeoutError("Chip communication timeout - chip remains busy")


    def _transfer(self, tx_data: bytes) -> bytes:
        """SPI bidirectional transfer.

        Corresponds to SPI write_readinto operation.

        :param tx_data: Data to transmit
        :type tx_data: bytes
        :returns: Received data (same length as tx_data)
        :rtype: bytes
        """
        raise NotImplementedError("_transfer() method not implemented in L1Transport subclass")


    def _read(self, length: int) -> bytes:
        """SPI read operation.

        Corresponds to SPI read operation.

        :param length: Number of bytes to read
        :type length: int
        :returns: Read data
        :rtype: bytes
        """
        raise NotImplementedError("_read() method not implemented in L1Transport subclass")


    def _cs_low(self) -> None:
        """Activate chip select (CS to logic 0)."""
        pass


    def _cs_high(self) -> None:
        """Deactivate chip select (CS to logic 1)."""
        pass
