PyTropicSquare Documentation
============================

Python library for communicating with the Tropic Square TROPIC01 secure element chip.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Overview
--------

PyTropicSquare provides both CPython and MicroPython implementations for interfacing
with the TROPIC01 secure element via SPI.

Key Features
------------

* **L1 Transport Layer**: Low-level read/write operations with CRC checks and retry logic
* **L2 Protocol Layer**: Packet framing, command/response handling, and chunking
* **L3 Commands**: High-level API for chip operations (ping, random, ECC, memory, etc.)
* **Secure Sessions**: X25519 key exchange with HKDF and AES-GCM encryption
* **Chip Information**: Parse chip ID, serial number, and configuration registers
* **Platform Support**: CPython and MicroPython implementations

Quick Start
-----------

MicroPython Example (ESP32)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from machine import SPI, Pin
   from tropicsquare import TropicSquare
   from tropicsquare.transports.spi import SPITransport

   spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
   cs = Pin(5, Pin.OUT)

   spi_transport = SPITransport(spi, cs)
   ts = TropicSquare(spi_transport)
   chip_id = ts.chipid

API Reference
-------------

.. toctree::
   :maxdepth: 3

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
