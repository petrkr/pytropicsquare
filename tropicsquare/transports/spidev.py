"""SPIDev Transport Implementation for Raspberry Pi

This module provides SPI transport implementation for Linux spidev interface
with manual GPIO chip select control.

Recommended Setup:
    Use general-purpose GPIO (e.g., GPIO 25, physical pin 22)::

        transport = SpiDevTransport(bus=0, device=0, cs_pin=25)

Alternative - Hardware CS Pins:
    GPIO 8 (CE0, pin 24) or GPIO 7 (CE1, pin 26)::

        transport = SpiDevTransport(bus=0, device=0, cs_pin=8)

.. note::
   Device tree overlay requirement depends on your hardware configuration:

   **No overlay needed** if:

   - You have NO other SPI devices connected to hardware CS pins (GPIO 8/7)
   - The kernel will toggle GPIO 8 (for /dev/spidev0.0) or GPIO 7 (for /dev/spidev0.1)
     during transfers, but this is harmless if nothing is connected there

   **Overlay REQUIRED** if:

   - You have other SPI devices connected to CE0 (GPIO 8) or CE1 (GPIO 7)
   - Without overlay, kernel will activate both your manual CS and hardware CS
     simultaneously, causing bus conflicts

   To disable hardware CS, add to /boot/firmware/config.txt and reboot:

   - ``dtoverlay=spi0-0cs`` - Don't claim any CS pins (recommended for manual CS)
   - ``dtoverlay=spi0-1cs,cs0_pin=<gpio>`` - Use only one CS pin (specify which)
   - ``dtoverlay=spi0-2cs,cs0_pin=<gpio>,cs1_pin=<gpio>`` - Remap CS pins
"""

import spidev
from gpiod import Chip, LineSettings
from gpiod.line import Direction, Value
from tropicsquare.transports import L1Transport


class SpiDevTransport(L1Transport):
    """L1 transport for Linux spidev interface with manual GPIO CS control.

    This transport uses the spidev library for SPI communication and gpiod
    for manual chip select control, providing precise timing control over
    the CS line.

    :param bus: SPI bus number (default: 0 for /dev/spidev0.x)
    :param device: SPI device number (default: 1 for CE1, use 0 for CE0)
    :param cs_pin: GPIO pin number for chip select (default: 25 for CE1, use 8 for CE0)
    :param max_speed_hz: SPI clock speed in Hz (default: 1000000 = 1 MHz)
    :param gpio_chip: GPIO chip device path (default: /dev/gpiochip0)

    Example::

        from tropicsquare.transports.spidev import SpiDevTransport
        from tropicsquare import TropicSquareCPython

        # Create transport for Raspberry Pi (using CE1 - no overlay needed)
        transport = SpiDevTransport(
            bus=0,
            device=1,
            cs_pin=25  # GPIO 25 (physical pin 22, CE1)
        )

        # Create TropicSquare instance
        ts = TropicSquareCPython(transport)

        try:
            # Use the chip
            chip_id = ts.chipid
            print(f"Chip ID: {chip_id}")
        finally:
            # Always cleanup
            transport.close()
    """

    def __init__(self,
                 bus: int = 0,
                 device: int = 1,
                 cs_pin: int = 25,
                 max_speed_hz: int = 1000000,
                 gpio_chip: str = "/dev/gpiochip0"):
        """Initialize SPIDev transport with manual GPIO CS control.

        :param bus: SPI bus number
        :param device: SPI device number
        :param cs_pin: GPIO pin number for chip select
        :param max_speed_hz: SPI clock speed in Hz
        :param gpio_chip: Path to GPIO chip device

        :raises OSError: If SPI or GPIO device cannot be opened
        """
        # Initialize SPI
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)

        # Configure SPI parameters (just like C library - no special CS flags)
        self._spi.mode = 0  # SPI_MODE_0: CPOL=0, CPHA=0
        self._spi.max_speed_hz = max_speed_hz
        self._spi.bits_per_word = 8
        self._spi.lsbfirst = False

        # Initialize GPIO for chip select
        self._cs_pin = cs_pin

        try:
            self._gpio_chip = Chip(gpio_chip)

            # Configure CS line as output with initial high state (inactive)
            line_settings = LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.ACTIVE  # Start with CS high (1 = inactive)
            )

            # Request CS line
            self._cs_request = self._gpio_chip.request_lines(
                consumer="tropicsquare-cs",
                config={cs_pin: line_settings}
            )
        except OSError as e:
            # None of the GPIO chips worked
            error_msg = f"Failed to open GPIO {cs_pin} for CS: {e}\n"
            error_msg += "Hint: Add 'dtoverlay=spi0-0cs' to /boot/firmware/config.txt and reboot"
            raise OSError(error_msg)

    def _transfer(self, tx_data: bytes) -> bytes:
        """SPI bidirectional transfer.

        Performs full-duplex SPI transfer using xfer2 method which
        simultaneously sends and receives data.

        :param tx_data: Data to transmit

        :returns: Received data (same length as tx_data)
        :rtype: bytes
        """
        # spidev xfer2() expects list of integers and returns list of integers
        rx_list = self._spi.xfer2(list(tx_data))
        return bytes(rx_list)


    def _read(self, length: int) -> bytes:
        """SPI read operation.

        Reads specified number of bytes from SPI bus by sending dummy bytes.

        :param length: Number of bytes to read

        :returns: Read data
        :rtype: bytes
        """
        # readbytes() sends 0x00 as dummy data and returns list of integers
        rx_list = self._spi.readbytes(length)
        return bytes(rx_list)


    def _cs_low(self) -> None:
        """Activate chip select (set CS to logic 0)."""
        self._cs_request.set_value(self._cs_pin, Value.INACTIVE)


    def _cs_high(self) -> None:
        """Deactivate chip select (set CS to logic 1)."""
        self._cs_request.set_value(self._cs_pin, Value.ACTIVE)


    def close(self) -> None:
        """Release SPI and GPIO resources.

        This method should be called when done using the transport to
        properly cleanup hardware resources. It's recommended to use
        the transport in a try/finally block or context manager.

        Example::

            transport = SpiDevTransport()
            try:
                # Use transport
                pass
            finally:
                transport.close()
        """
        # Release GPIO
        try:
            self._cs_request.release()
        except Exception:
            pass  # Ignore errors during cleanup

        try:
            self._gpio_chip.close()
        except Exception:
            pass  # Ignore errors during cleanup

        # Close SPI
        try:
            self._spi.close()
        except Exception:
            pass  # Ignore errors during cleanup
