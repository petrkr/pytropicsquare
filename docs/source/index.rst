PyTropicSquare Documentation
============================

Python library for communicating with the Tropic Square TROPIC01 secure element chip.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Overview
--------

PyTropicSquare provides both CPython and MicroPython implementations for interfacing
with the TROPIC01 secure element via SPI.

Key Features
------------

* **L2 Protocol Layer**: Low-level SPI communication with CRC validation and retry logic
* **L3 Commands**: High-level API for chip operations (ping, random, ECC, memory, etc.)
* **Secure Sessions**: X25519 key exchange with HKDF and AES-GCM encryption
* **Chip Information**: Parse chip ID, serial number, and configuration registers
* **Platform Support**: CPython and MicroPython implementations

Quick Start
-----------

CPython Example
^^^^^^^^^^^^^^^

.. code-block:: python

   from tropicsquare import TropicSquare

   # Auto-detects platform (CPython/MicroPython)
   ts = TropicSquare(spi, cs)

   # Read chip information
   chip_id = ts.chipid
   print(f"Chip ID: {chip_id}")

   # Start secure session
   ts.start_secure_session(pkey_index, priv_key, pub_key)

   # Execute commands
   random_bytes = ts.get_random(32)
   ping_response = ts.ping(b"Hello TROPIC01")

MicroPython Example (ESP32)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from machine import SPI, Pin
   from tropicsquare import TropicSquare

   spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
   cs = Pin(5, Pin.OUT)

   ts = TropicSquare(spi, cs)
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
