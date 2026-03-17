MicroPython Port
================

The MicroPython port provides an optimized implementation of PyTropicSquare for embedded systems.
It includes custom cryptographic implementations optimized for resource-constrained environments.

.. currentmodule:: tropicsquare.ports.micropython

.. automodule:: tropicsquare.ports.micropython
   :members:
   :undoc-members:
   :show-inheritance:

Platform Requirements
---------------------

* MicroPython 1.25+
* ESP32 or compatible board
* Sufficient flash and RAM for crypto operations

Installation
------------

Connect your board to Wi-Fi and install the package with ``mip``:

.. code-block:: python

   from network import WLAN

   w = WLAN()
   w.active(1)
   w.connect(ssid, psk)

   import mip
   mip.install("https://github.com/petrkr/pytropicsquare/releases/download/<release-tag>/pytropicsquare-<version>-mip.json")

Example for release ``v0.1.0``:

.. code-block:: python

   import mip
   mip.install("https://github.com/petrkr/pytropicsquare/releases/download/v0.1.0/pytropicsquare-0.1.0-mip.json")

Features
--------

* Embedded cryptographic implementations
* Optimized for resource-constrained environments
* Support for SPI, UART, and network transports
* ESP32 and other MicroPython boards

Cryptographic Implementation
----------------------------

The MicroPython port includes custom implementations of:

* X25519 key exchange
* AES-GCM encryption
* HKDF key derivation
* SHA-256 hashing

See Also
--------

* :doc:`cpython` - CPython implementation
* :doc:`/api/core` - Base TropicSquare class
