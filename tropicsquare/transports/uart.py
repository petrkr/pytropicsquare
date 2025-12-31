"""UART SPI Transport Implementation

"""

import sys
from tropicsquare.transports import L1Transport


class UartTransport(L1Transport):
    """L1 transport for UART

    :param uart: UART interface object (e.g., machine.UART instance)
    """


    def __init__(self, port: str, baudrate: int = 115200):
        """Initialize UART transport.

        :param port: UART port name (e.g. /dev/ttyACM0)
        :param baudrate: Baud rate for UART communication
        """

        if sys.implementation.name == "micropython":
            if sys.platform == "linux":
                import os
                import termios
                # For micropython on linux open serial as file
                fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
                termios.setraw(fd) # Set RAW
                os.close(fd)
                self._port = open(port, "r+b", buffering=0) # Reopen serial device
                self._flush = False # Micropython file does not supports flush
            else:
                raise RuntimeError("Unsupported platform for Micropython: {}".format(sys.platform))

        elif sys.implementation.name == "cpython":
            from serial import Serial
            self._port = Serial(port, baudrate)
            self._flush = True
        else:
            raise RuntimeError("Unsupported Python implementation: {}".format(sys.implementation.name))


    def _transfer(self, tx_data: bytes) -> bytes:
        """SPI transfer using write_readinto.

        :param tx_data: Data to transmit

        :returns: Received data
        """
        # Write data
        hex_data = tx_data.hex().upper() + "x\n"
        self._port.write(hex_data.encode())
        if self._flush: self._port.flush()

        # Read data
        hex_line = self._port.readline().decode().strip()
        rx_buffer = bytes.fromhex(hex_line)

        return rx_buffer


    def _read(self, length: int) -> bytes:
        """SPI read operation.

        :param length: Number of bytes to read

        :returns: Read data
        """
        # Send read command with length of dummy bytes
        self._port.write(b"00" * length + b"x\n")
        if self._flush: self._port.flush()

        # Read data
        hex_line = self._port.readline().decode().strip()
        data = bytes.fromhex(hex_line)
        return data


    def _set_cs(self, state: bool):
        self._port.write("CS={}\n".format("1" if state else "0").encode())
        if self._flush: self._port.flush()
        self._port.readline() # read OK


    def _cs_low(self) -> None:
        self._set_cs(False)


    def _cs_high(self) -> None:
        self._set_cs(True)


    def _close(self):
        self._port.close()
