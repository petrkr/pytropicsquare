
import sys

from tropicsquare.ports.cpython import TropicSquareCPython
from tropicsquare.exceptions import *
from uartspi import UartSPI, TropicUartSpiCS

pkey_index_0 = 0x00 # Slot 0
# Default factory pairing keys
# Sample keys batch 1
#sh0priv = [0xd0,0x99,0x92,0xb1,0xf1,0x7a,0xbc,0x4d,0xb9,0x37,0x17,0x68,0xa2,0x7d,0xa0,0x5b,0x18,0xfa,0xb8,0x56,0x13,0xa7,0x84,0x2c,0xa6,0x4c,0x79,0x10,0xf2,0x2e,0x71,0x6b]
#sh0pub  = [0xe7,0xf7,0x35,0xba,0x19,0xa3,0x3f,0xd6,0x73,0x23,0xab,0x37,0x26,0x2d,0xe5,0x36,0x08,0xca,0x57,0x85,0x76,0x53,0x43,0x52,0xe1,0x8f,0x64,0xe6,0x13,0xd3,0x8d,0x54]

# Sample keys batch 2
sh0priv = [0x28,0x3F,0x5A,0x0F,0xFC,0x41,0xCF,0x50,0x98,0xA8,0xE1,0x7D,0xB6,0x37,0x2C,0x3C,0xAA,0xD1,0xEE,0xEE,0xDF,0x0F,0x75,0xBC,0x3F,0xBF,0xCD,0x9C,0xAB,0x3D,0xE9,0x72]
sh0pub =  [0xF9,0x75,0xEB,0x3C,0x2F,0xD7,0x90,0xC9,0x6F,0x29,0x4F,0x15,0x57,0xA5,0x03,0x17,0x80,0xC9,0xAA,0xFA,0x14,0x0D,0xA2,0x8F,0x55,0xE7,0x51,0x57,0x37,0xB2,0x50,0x2C]

def main():
    port = sys.argv[1]

    # L1 layer
    spi = UartSPI(port)
    cs = TropicUartSpiCS(spi)

    ts = TropicSquareCPython(spi, cs)

    try:
        # Get chip information (outside session)
        print("Chip ID: {}".format(ts.chipid.hex()))
        print("Spect FW version: {}".format(ts.spect_fw_version))
        print("RISCV FW version: {}".format(ts.riscv_fw_version))
        
        try:
            print("FW Bank: {}".format(ts.fw_bank))
        except TropicSquareError as e:
            print("FW Bank unavailable: {}".format(e))

        print("RAW Certificate: {}".format(ts.certificate.hex()))
        print("Cert Public Key: {}".format(ts.public_key.hex()))

        print("Starting secure session with context manager...")
        ts.start_secure_session(pkey_index_0, bytes(sh0priv), bytes(sh0pub))
        print("Secure session established!")

        # Test ping with long message (chunk required)
        resp = ts.ping(b"Very long ping! Chunk required..." * 5)
        print("Ping response: {}".format(resp))

        # Test ECC key operations
        try:
            print("ECC Pubkey #0: {}".format(ts.ecc_key_read(0)[2].hex()))
            print("ECC Pubkey #1: {}".format(ts.ecc_key_read(1)[2].hex()))
        except TropicSquareECCError as e:
            print("ECC key read error: {}".format(e))

        # Test signing operations
        try:
            sign = ts.eddsa_sign(0, b"Hello Tropic Square From CPython!")
            print("EdDSA signature by key #0:")
            print("  R: {}".format(sign[0].hex()))
            print("  S: {}".format(sign[1].hex()))
        except TropicSquareECCError as e:
            print("EdDSA signing error: {}".format(e))

        # Test ECDSA with SHA256 of "Ahoj"
        try:
            sign = ts.ecdsa_sign(1, b'\xd2z\x7f\x03\x8bq^\x0b\x8aC\x8a\tpN1\x02\x15\nAX\xa7\xf17+\xb6\xe0\xe6X\xc0\x0e|\n')
            print("ECDSA signature by key #1:")
            print("  R: {}".format(sign[0].hex()))
            print("  S: {}".format(sign[1].hex()))
        except TropicSquareECCError as e:
            print("ECDSA signing error: {}".format(e))

        # Test monotonic counter
        print("Initializing monotonic counter #0 with value 3")
        ts.mcounter_init(0, 3)
        print("Counter value: {}".format(ts.mcounter_get(0)))

        print("Updating monotonic counter")
        ts.mcounter_update(0)
        print("Counter value after update: {}".format(ts.mcounter_get(0)))

        # Test random number generation
        try:
            for i in range(4):
                random = ts.get_random(4)
                print("Random #{}: {}".format(i+1, random.hex()))
        except TropicSquareError as e:
            print("Random generation error: {}".format(e))

        # Get device log
        print("Device log:")
        print(ts.get_log())

    except TropicSquareAlarmError as e:
        print("ALARM: Chip is in alarm state: {}".format(e))
    except TropicSquareHandshakeError as e:
        print("HANDSHAKE ERROR: {}".format(e))
    except TropicSquareTimeoutError as e:
        print("TIMEOUT: {}".format(e))
    except TropicSquareCRCError as e:
        print("CRC ERROR: {}".format(e))
    except TropicSquareError as e:
        print("TROPICSQUARE ERROR: {}".format(e))
    except Exception as e:
        print("UNEXPECTED ERROR: {}".format(e))

if __name__ == "__main__":
    main()
