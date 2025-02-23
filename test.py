
import sys

#from tropicsquare.ports.micropython import TropicSquareMicroPython
from tropicsquare.ports.networkspi import TropicSquareNetworkSPI


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    ts = TropicSquareNetworkSPI(host, port)

    print("Spect FW version: {}".format(ts.spect_fw_version))
    print("RISCV FW version: {}".format(ts.riscv_fw_version))
    print("Chip ID: {}".format(ts.chipid))
    try:
        print("FW Bank: {}".format(ts.fw_bank))
    except Exception as e:
        print("Exception: {}".format(e))

    cert = ts.certificate
    print("Certificate: {}".format(cert))


if __name__ == "__main__":
    main()
