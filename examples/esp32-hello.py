
"""ESP32 MicroPython Example for Tropic Square TROPIC01 Chip
"""

from machine import SPI, Pin

from tropicsquare import TropicSquare
from tropicsquare.transports.spi import SpiTransport
from tropicsquare.constants.pairing_keys import *
from tropicsquare.exceptions import *


pkey_index_0 = FACTORY_PAIRING_KEY_INDEX

# Default factory pairing keys
# sh0priv = FACTORY_PAIRING_PRIVATE_KEY_ENG_SAMPLE
# sh0pub  = FACTORY_PAIRING_PUBLIC_KEY_ENG_SAMPLE

sh0priv = FACTORY_PAIRING_PRIVATE_KEY_PROD0
sh0pub  = FACTORY_PAIRING_PUBLIC_KEY_PROD0


def main():
    spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
    cs = Pin(5, Pin.OUT)

    ts = TropicSquare(SpiTransport(spi, cs))

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
        ts.start_secure_session(pkey_index_0, sh0priv, sh0pub)
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
