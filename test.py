
import sys

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


#    with open("tropic.crt", "rb") as f:
#        ts._certificate = f.read()

    print("RAW Certificate: {}".format(ts.certificate))
    print("Cert Public Key (PyTropicSquare): {}".format(ts.public_key))

    print("Starting secure session...")
    ts.start_secure_session(pkey_index_0, bytes(sh0priv), bytes(sh0pub))

    #resp = ts.ping(b"Very long ping! Chunk required..." * 5)
    #print("Ping: {}".format(resp))

    #print("ECC Pubkey #0: {}".format(ts.ecc_key_read(0)[2].hex()))
    #print("ECC Pubkey #1: {}".format(ts.ecc_key_read(1)[2].hex()))

    #sign = ts.eddsa_sign(0, b"Hello Tropic Square From MicroPython!")
    #print("Sign message by key #0")
    #print("  R: {}".format(sign[0].hex()))
    #print("  S: {}".format(sign[1].hex()))

    # SHA256 of "Ahoj"
    #sign = ts.ecdsa_sign(1, b'\xd2z\x7f\x03\x8bq^\x0b\x8aC\x8a\tpN1\x02\x15\nAX\xa7\xf17+\xb6\xe0\xe6X\xc0\x0e|\n')
    #print("Sign hash by key #1")
    #print("  R: {}".format(sign[0].hex()))
    #print("  S: {}".format(sign[1].hex()))

    #print("Initialzize monotonic counter by number 3")
    #ts.mcounter_init(0, 3)

    #print("Counter value: {}".format(ts.mcounter_get(0)))

    #print("Update monotonic counter")
    #ts.mcounter_update(0)
    #print("Counter value: {}".format(ts.mcounter_get(0)))

    try:
        pass
        #resp = ts.ping(b"Hello Tropic Square From MicroPython!")
        #print("Ping: {}".format(resp))

        #resp = ts.ping(b"Second Ping")
        #print("Ping: {}".format(resp))

        #for _ in range(4):
        #    random = ts.get_random(1)
        #    print("Random: {}".format(random))

    except Exception as e:
        print("Exception: {}".format(e))


    print("Log")
    print(ts.get_log())

if __name__ == "__main__":
    main()
