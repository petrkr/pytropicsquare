
from .. import TropicSquare
import socket
from random import randbytes

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256


class NetworkSPI:
    COMMAND_READ = b'\x01'
    COMMAND_READINTO = b'\x02'
    COMMAND_WRITE = b'\x04'
    COMMAND_WRITE_READINTO = b'\x08'

    COMMAND_CS_LOW = b'\x10'
    COMMAND_CS_HIGH = b'\x20'


    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))


    def write_readinto(self, write_buf, read_buf):
        command = self.COMMAND_WRITE_READINTO
        data = bytes(write_buf)
        length = len(data)
        packet = command + length.to_bytes(4, 'big') + data
        self.sock.sendall(packet)
        
        received = b''
        while len(received) < length:
            chunk = self.sock.recv(length - len(received))
            if not chunk:
                raise RuntimeError("Connection lost during SPI transfer")
            received += chunk
        for i in range(len(received)):
            read_buf[i] = received[i]


    def readinto(self, read_buf):
        command = self.COMMAND_READINTO
        length = len(read_buf)
        packet = command + length.to_bytes(4, 'big')
        self.sock.sendall(packet)
        
        received = b''
        while len(received) < length:
            chunk = self.sock.recv(length - len(received))
            if not chunk:
                raise RuntimeError("Connection lost during SPI transfer")
            received += chunk
   
        for i in range(len(received)):
            read_buf[i] = received[i]


    def read(self, length):
        command = self.COMMAND_READ
        packet = command + length.to_bytes(4, 'big')
        self.sock.sendall(packet)
        
        received = b''
        while len(received) < length:
            chunk = self.sock.recv(length - len(received))
            if not chunk:
                raise Exception("Connection lost during SPI transfer")
            received += chunk

        return received


    def write(self, data):
        command = self.COMMAND_WRITE
        length = len(data)
        packet = command + length.to_bytes(4, "big") + data
        self.sock.sendall(packet)


    def set_cs(self, state: bool):
        """Sends a command (0x01) to set the chip select state.
           The state is sent as 1 byte (0 for low, 1 for high)."""
        command = self.COMMAND_CS_HIGH if state else self.COMMAND_CS_LOW
        self.sock.sendall(command)

        ack = self.sock.recv(1)
        if ack != b'\x00':
            raise RuntimeError("Chip select command failed, ack: " + str(ack))


    def close(self):
        self.sock.close()


class TropicSquareNetworkSPI(TropicSquare):
    def __init__(self, host, port):
        self._spi = NetworkSPI(host, port)
        super().__init__()


    def _spi_cs(self, value):
        self._spi.set_cs(value)


    def _spi_write(self, data):
        self._spi.write(data)


    def _spi_read(self, len: int) -> bytes:
        return self._spi.read(len)


    def _spi_readinto(self, buffer: bytearray):
        self._spi.readinto(buffer)


    def _spi_write_readinto(self, tx_buffer, rx_buffer: bytearray):
        self._spi.write_readinto(tx_buffer, rx_buffer)


    def _random(self, length):
        # length is consider we return 4 bytes
        return randbytes(length*4)


    def _get_ephemeral_keypair(self):
        ehpriv = X25519PrivateKey.generate()
        ehpubraw = ehpriv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        ehprivraw = ehpriv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

        return (ehprivraw, ehpubraw)


    def _hkdf(self, salt, shared_secret, length = 1):
        result = HKDF(algorithm=SHA256(),
                    length=length * 32,
                    salt=salt,
                    info=None).derive(shared_secret)

        if length > 1:
            return [result[i*32:(i+1)*32] for i in range(length)]
        else:
            return result
