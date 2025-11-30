from serial import Serial

class TropicUartSpiCS:
    def __init__(self, uart_spi):
        self.pin = uart_spi.set_cs

    def value(self, value):
        self.pin(value)


class UartSPI:
    def __init__(self, port, baudrate=115200):
        self.port = Serial(port, baudrate)


    def write_readinto(self, write_buf, read_buf):
        self.write(write_buf)
        self.readinto(read_buf)


    def readinto(self, read_buf):
        hex_line = self.port.readline().decode().strip()
        data = bytes.fromhex(hex_line)
        read_buf[:len(read_buf)] = data


    def read(self, length):
        buffer = bytearray(length)
        self.write_readinto(buffer, buffer)
        return buffer


    def write(self, data):
        hex_data = data.hex().upper() + "x\n"
        self.port.write(hex_data.encode())
        self.port.flush()


    def set_cs(self, state: bool):
        self.port.write("CS={}\n".format("1" if state else "0").encode())
        self.port.flush()
        self.port.readline() # read OK


    def close(self):
        self.port.close()
