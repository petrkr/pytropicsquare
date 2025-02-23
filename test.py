
import sys

#from tropicsquare.ports.micropython import TropicSquareMicroPython
from tropicsquare.ports.networkspi import TropicSquareNetworkSPI


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    ts = TropicSquareNetworkSPI(host, port)
    cert = ts.certificate
    print(cert)

    with open("tropic.crt", "wb") as f:
        f.write(cert)

    #print(ts.riscv_fw_version)


if __name__ == "__main__":
    main()
