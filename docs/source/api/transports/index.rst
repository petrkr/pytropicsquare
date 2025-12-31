Transport Layer
===============

The transport layer (L1) provides the physical communication interface with the TROPIC01 chip.
PyTropicSquare supports multiple transport options to accommodate different platforms and use cases.

Available Transports
--------------------

.. autosummary::
   :nosignatures:

   tropicsquare.transports.spi.SpiTransport
   tropicsquare.transports.uart.UartTransport
   tropicsquare.transports.network.NetworkSpiTransport
   tropicsquare.transports.tcp.TcpTransport

Transport Selection Guide
--------------------------

* **SPI Transport** - Direct hardware connection via SPI bus (MicroPython ESP32)
* **UART Transport** - Serial communication via UART (CPython, MicroPython Unix only - NOT ESP32)
* **Network-SPI Transport** - SPI over network for remote chips (MicroPython ESP32)
* **TCP Transport** - TCP connection to Tropic01 model server (development/testing)

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 1

   base
   spi
   uart
   network
   tcp
