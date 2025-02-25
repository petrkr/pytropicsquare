import sys
from time import sleep

from networkspi import NetworkSPI, DummyNetworkSpiCSPin
from tropicsquare.crc import CRC


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])

    spi = NetworkSPI(host, port)
    cs = DummyNetworkSpiCSPin(spi)

    cs.value(1)

    chip_status = bytearray(1)

    cs.value(0)
    # Request ID - Get Info
    spi.write_readinto(b'\x01', chip_status)
    print("Chip status: {}".format(hex(chip_status[0])))

    # Get info length
    spi.write(b'\x02')

    # Chip ID, Datachunk 0
    spi.write(b'\x01\x00')

    # CRC
    spi.write(b'\x2b\x92')

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
    calccrc = CRC.crc16(resstatus.to_bytes(1) + reslen.to_bytes(1) + (data or b''))

    print("Response data: {}".format(data))
    print("Response CRC (Recv): {}".format(rescrc))
    print("Response CRC (Calc): {}".format(calccrc))
    print("CRC match: {}".format(rescrc == calccrc))


    cs.value(1)
