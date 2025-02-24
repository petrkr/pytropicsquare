
import sys

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tropicsquare.ports.python import TropicSquarePython
from networkspi import NetworkSPI, DummyNetworkSpiCSPin


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    # L1 layer
    spi = NetworkSPI(host, port)
    cs = DummyNetworkSpiCSPin(spi)

    ts = TropicSquarePython(spi, cs)

    print("Spect FW version: {}".format(ts.spect_fw_version))
    print("RISCV FW version: {}".format(ts.riscv_fw_version))
    print("Chip ID: {}".format(ts.chipid))
    try:
        print("FW Bank: {}".format(ts.fw_bank))
    except Exception as e:
        print("Exception: {}".format(e))


    rawcert = ts.certificate
    print("RAW Certificate: {}".format(rawcert))

    cert = x509.load_der_x509_certificate(rawcert, default_backend())
    pubkey = cert.public_key()

    print("Cert Public Key (PyTropicSquare): {}".format(ts.public_key))
    print("Cert Public Key (cryptography): {}".format(pubkey.public_bytes(Encoding.Raw, PublicFormat.Raw)))


if __name__ == "__main__":
    main()
