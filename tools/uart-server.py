from machine import SPI, Pin
import sys

PIN_SCK = 47
PIN_MOSI = 21
PIN_MISO = 9
PIN_CS = 15

LED_ACTIVE_HIGH = True
PIN_LED_RX = 48
PIN_LED_TX = 14


# Adjust pins/SPI bus for your board wiring.
spi = SPI(
    1,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(PIN_SCK),
    mosi=Pin(PIN_MOSI),
    miso=Pin(PIN_MISO),
)
cs = Pin(PIN_CS, Pin.OUT, value=1)  # idle HIGH (inactive)


class ActivityLed:
    def __init__(self, pin_no):
        self.pin = None if pin_no is None else Pin(pin_no, Pin.OUT)
        self.off()

    def on(self):
        if self.pin is None:
            return
        self.pin.value(1 if LED_ACTIVE_HIGH else 0)

    def off(self):
        if self.pin is None:
            return
        self.pin.value(0 if LED_ACTIVE_HIGH else 1)

led_rx = ActivityLed(PIN_LED_RX)
led_tx = ActivityLed(PIN_LED_TX)


def cs_set(active):
    # Protocol uses 1 == active == LOW, 0 == idle == HIGH.
    cs.value(0 if active else 1)


def cs_get():
    return 1 if cs.value() == 0 else 0


def parse_hex_line(line):
    skip_begin = line[:1] in ("x", "\\")
    skip_end = line[-1:] in ("x", "\\")
    if skip_begin:
        line = line[1:]
    if skip_end and line:
        line = line[:-1]
    hex_txt = "".join(line.split())
    if len(hex_txt) == 0 or (len(hex_txt) & 1):
        return None
    try:
        tx = bytes.fromhex(hex_txt)
    except ValueError:
        return None
    return tx, skip_begin, skip_end


def stdout_write(text):
    led_tx.on()
    sys.stdout.write(text)
    led_tx.off()


while True:
    line = sys.stdin.readline()
    if not line:
        continue
    led_rx.on()
    line = line.strip()
    led_rx.off()
    if not line:
        continue

    # Command path
    if line.upper().startswith("CS"):
        if "=" in line:
            value = line.split("=", 1)[1].strip()
            if value == "0":
                cs_set(False)
                stdout_write("OK\n")
            elif value == "1":
                cs_set(True)
                stdout_write("OK\n")
            else:
                stdout_write("ERROR: invalid parameter\n")
        else:
            stdout_write("CS: %d\nOK\n" % cs_get())
        continue

    # SPI data path
    parsed = parse_hex_line(line)
    if parsed is None:
        stdout_write("ERROR: unknown command\n")
        continue

    tx, skip_begin, skip_end = parsed

    if not skip_begin:
        cs_set(True)

    rx = bytearray(len(tx))
    spi.write_readinto(tx, rx)

    if not skip_end:
        cs_set(False)

    stdout_write("".join("%02X" % b for b in rx) + "\n")
