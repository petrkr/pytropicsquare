SPIDev Transport
================

The SPIDev transport provides SPI communication with the TROPIC01 chip on Linux systems using the spidev kernel module with manual GPIO chip select control.

.. currentmodule:: tropicsquare.transports.spidev

.. automodule:: tropicsquare.transports.spidev
   :members:
   :undoc-members:
   :show-inheritance:

Platform Support
----------------

* **Raspberry Pi** (all models): Full support via ``spidev`` and ``gpiod``
* **Linux with spidev**: Any Linux system with spidev kernel module

Requirements
------------

* Python packages: ``spidev>=3.5``, ``gpiod>=2.0``
* User permissions: Add user to ``spi`` and ``gpio`` groups
* Device tree overlay: Only required if other SPI devices on CE0/CE1 (see module docstring)

Hardware Setup
--------------

* **SPI Bus**: Use ``/dev/spidev0.0`` (SPI0)
* **Chip Select**: Any free GPIO (default: GPIO 25, physical pin 22)
* **MISO/MOSI/SCK**: Standard SPI0 pins (GPIO 9/10/11)

Example Usage
-------------

.. code-block:: python

   from tropicsquare import TropicSquare
   from tropicsquare.transports.spidev import SpiDevTransport

   # Create transport
   transport = SpiDevTransport(
       bus=0,
       device=0,
       cs_pin=25,  # GPIO 25 (or any free GPIO)
       max_speed_hz=1000000
   )

   # Create TropicSquare instance
   ts = TropicSquare(transport)

   try:
       # Use the chip
       chip_id = ts.chipid
       print(f"Chip ID: {chip_id}")
   finally:
       # Always cleanup
       transport.close()

See Also
--------

* :doc:`spi` - MicroPython SPI transport
* :doc:`uart` - UART transport alternative
* Example: ``examples/rpi_spidev_quickstart.py``
