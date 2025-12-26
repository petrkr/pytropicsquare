"""UART SPI Transport Implementation

"""

from serial import Serial

from tropicsquare.transports import L1Transport


class UartTransport(L1Transport):
    """L1 transport for UART

    :param uart: UART interface object (e.g., machine.UART instance)
    """


    def __init__(self, port, baudrate=115200):
        """Initialize UART transport.

        :param port: UART port name (e.g. /dev/ttyACM0)
        :param baudrate: Baud rate for UART communication
        """
        self.port = Serial(port, baudrate)


    def _transfer(self, tx_data: bytes) -> bytes:
        """SPI transfer using write_readinto.

        :param tx_data: Data to transmit
        :type tx_data: bytes
        :returns: Received data
        :rtype: bytes
        """
        # Write data
        hex_data = tx_data.hex().upper() + "x\n"
        self.port.write(hex_data.encode())
        self.port.flush()

        # Read data
        hex_line = self.port.readline().decode().strip()
        rx_buffer = bytes.fromhex(hex_line)

        return rx_buffer


    def _read(self, length: int) -> bytes:
        """SPI read operation.

        :param length: Number of bytes to read
        :type length: int
        :returns: Read data
        :rtype: bytes
        """
        # Send read command with length of dummy bytes
        self.port.write(b"00" * length + b"x\n")
        self.port.flush()

        # Read data
        hex_line = self.port.readline().decode().strip()
        data = bytes.fromhex(hex_line)
        return data


    def _set_cs(self, state: bool):
        self.port.write("CS={}\n".format("1" if state else "0").encode())
        self.port.flush()
        self.port.readline() # read OK


    def _cs_low(self) -> None:
        self._set_cs(False)


    def _cs_high(self) -> None:
        self._set_cs(True)


    def _close(self):
        self.port.close()
