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

* MicroPython 1.19+ (recommended: 1.20+)
* ESP32 or compatible board
* Sufficient flash and RAM for crypto operations

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
