import sys
from time import sleep

from tropicsquare.ports.networkspi import NetworkSPI
from tropicsquare.crc16 import CRC16

class dummyPin:
    def __init__(self, networkSpi):
        self._spi = networkSpi


    def value(self, value):
        self._spi.set_cs(value)


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])

    spi = NetworkSPI(host, port)
    crc = CRC16()
    cs = dummyPin(spi)

    # 0x2b92 - Request CRC
    print(crc.crc16(b'\x01\x02\x02\x00'))

    # 0x0608 - Response CRC
    print(crc.crc16(b'\x7C\x00'))

    cs.value(1)

    chip_status = bytearray(1)

    cs.value(0)
    # Request ID - Get Info
    spi.write_readinto(b'\x01', chip_status)
    print("Chip status: {}".format(hex(chip_status[0])))

    # Get info length
    spi.write(b'\x02')

    # Chip ID, Datachunk 0
    spi.write(b'\x02\x00')

    # CRC
    spi.write(b'\x2b\x98')

    cs.value(1)

    sleep(0.1)
    cs.value(0)
    # Request response
    spi.write_readinto(b'\xAA', chip_status)
    print("Chip status: {}".format(hex(chip_status[0])))

    # Get response status
    resstatus = spi.read(1)[0]
    print("Status: {}".format(hex(resstatus)))

    # Response length
    reslen = spi.read(1)[0]
    print("Response length: {}".format(reslen))

    if reslen:
        data = spi.read(reslen)
    else:
        data = None

    rescrc = spi.read(2)

    print("Response data: {}".format(data))
    print("Response CRC: {}".format(rescrc))

    cs.value(1)
