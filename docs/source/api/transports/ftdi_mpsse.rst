FTDI MPSSE Transport
====================

The FTDI MPSSE transport provides SPI communication with the TROPIC01 chip over
an FTDI USB-to-SPI bridge such as FT2232H or FT2232HL.

.. currentmodule:: tropicsquare.transports.ftdi_mpsse

.. automodule:: tropicsquare.transports.ftdi_mpsse
   :members:
   :undoc-members:
   :show-inheritance:

Platform Support
----------------

* **CPython**: Full support via ``pyftdi``
* **FTDI MPSSE devices**: Tested with FT2232HL

Requirements
------------

* Python package: ``pyftdi``
* FTDI device with MPSSE support

Hardware Setup
--------------

* **AD0**: SCK
* **AD1**: MOSI
* **AD2**: MISO
* **AD3**: CS
* **GND**: GND

URL Selection
-------------

For a single FTDI device, a generic URL such as ``ftdi://ftdi:2232h/1`` is
usually sufficient.

If multiple FTDI devices are connected, prefer a serial-qualified URL such as
``ftdi://ftdi:2232:OL4F9NTA/1``.

Example Usage
-------------

.. code-block:: python

   from pyftdi.spi import SpiController
   from tropicsquare import TropicSquare
   from tropicsquare.transports.ftdi_mpsse import FtdiMpsseTransport

   controller = SpiController(cs_count=1)
   controller.configure("ftdi://ftdi:2232h/1")
   spi = controller.get_port(cs=0, freq=1000000, mode=0)

   transport = FtdiMpsseTransport(spi)

   ts = TropicSquare(transport)

   try:
       print(ts.chip_id)
   finally:
       controller.close()

See Also
--------

* :doc:`spidev` - Linux SPI transport
* :doc:`spi` - MicroPython SPI transport
* Example: ``examples/ftdi_mpsse_quickstart.py``
