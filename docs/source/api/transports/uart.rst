UART Transport
==============

The UART transport provides serial communication with the TROPIC01 chip via UART interface.

.. currentmodule:: tropicsquare.transports.uart

.. automodule:: tropicsquare.transports.uart
   :members:
   :undoc-members:
   :show-inheritance:

Platform Support
----------------

* **CPython**: Full support via ``pyserial`` library
* **MicroPython Unix/Linux**: Supported (direct file I/O)
* **MicroPython ESP32**: **NOT supported** (raises RuntimeError)

.. note::
   For ESP32, use :doc:`spi` or :doc:`network` transport instead.

See Also
--------

* :doc:`spi` - SPI transport for ESP32
* :doc:`network` - Network-based transport for ESP32
