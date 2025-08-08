
import sys

from tropicsquare.ports.micropython import TropicSquareMicroPython
from tropicsquare.exceptions import *
from machine import SPI, Pin


# Default factory pairing keys
pkey_index_0 = 0x00 # Slot 0
sh0priv = [0xd0,0x99,0x92,0xb1,0xf1,0x7a,0xbc,0x4d,0xb9,0x37,0x17,0x68,0xa2,0x7d,0xa0,0x5b,0x18,0xfa,0xb8,0x56,0x13,0xa7,0x84,0x2c,0xa6,0x4c,0x79,0x10,0xf2,0x2e,0x71,0x6b]
sh0pub  = [0xe7,0xf7,0x35,0xba,0x19,0xa3,0x3f,0xd6,0x73,0x23,0xab,0x37,0x26,0x2d,0xe5,0x36,0x08,0xca,0x57,0x85,0x76,0x53,0x43,0x52,0xe1,0x8f,0x64,0xe6,0x13,0xd3,0x8d,0x54]


def main():
    spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
    cs = Pin(5, Pin.OUT)

    ts = TropicSquareMicroPython(spi, cs)

    try:
        # Get chip information
        print("Spect FW version: {}".format(ts.spect_fw_version))
        print("RISCV FW version: {}".format(ts.riscv_fw_version))
        print("Chip ID: {}".format(ts.chipid.hex()))

        try:
            print("FW Bank: {}".format(ts.fw_bank))
        except TropicSquareError as e:
            print("FW Bank unavailable: {}".format(e))

        print("RAW Certificate: {}".format(ts.certificate.hex()))
        print("Cert Public Key: {}".format(ts.public_key.hex()))

        # Start secure session
        print("Starting secure session...")
        ts.start_secure_session(pkey_index_0, bytes(sh0priv), bytes(sh0pub))
        print("Secure session established!")

        # Test ping command
        resp = ts.ping(b"Hello Tropic Square From MicroPython!")
        print("Ping response: {}".format(resp))

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
    finally:
        # Always try to clean up session
        try:
            ts.abort_secure_session()
            print("Session terminated")
        except:
            pass


if __name__ == "__main__":
    main()
