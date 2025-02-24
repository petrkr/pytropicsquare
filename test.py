
import sys

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tropicsquare.ports.cpython import TropicSquareCPython
from networkspi import NetworkSPI, DummyNetworkSpiCSPin

# Default factory pairing keys
pkey_index_0 = 0x00 # Slot 0
sh0priv = [0xd0,0x99,0x92,0xb1,0xf1,0x7a,0xbc,0x4d,0xb9,0x37,0x17,0x68,0xa2,0x7d,0xa0,0x5b,0x18,0xfa,0xb8,0x56,0x13,0xa7,0x84,0x2c,0xa6,0x4c,0x79,0x10,0xf2,0x2e,0x71,0x6b]
sh0pub  = [0xe7,0xf7,0x35,0xba,0x19,0xa3,0x3f,0xd6,0x73,0x23,0xab,0x37,0x26,0x2d,0xe5,0x36,0x08,0xca,0x57,0x85,0x76,0x53,0x43,0x52,0xe1,0x8f,0x64,0xe6,0x13,0xd3,0x8d,0x54]


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    # L1 layer
    spi = NetworkSPI(host, port)
    cs = DummyNetworkSpiCSPin(spi)

    ts = TropicSquareCPython(spi, cs)

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
