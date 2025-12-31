TCP Transport
=============

The TCP transport connects to the Tropic01 model server for development and testing purposes.
This allows testing PyTropicSquare without physical hardware.

.. currentmodule:: tropicsquare.transports.tcp

.. automodule:: tropicsquare.transports.tcp
   :members:
   :undoc-members:
   :show-inheritance:

Model Server
------------

The Tropic01 model server simulates chip behavior for:

* Development without hardware
* Automated testing
* CI/CD integration

Platform Support
----------------

* **CPython**: Full support
* **MicroPython**: Supported with network connectivity

See Also
--------

* :doc:`network` - Network-SPI transport for real chips
* :doc:`spi` - Direct hardware SPI transport
