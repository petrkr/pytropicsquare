Platform Ports
==============

PyTropicSquare provides platform-specific implementations for both CPython and MicroPython environments.
Each port implements the cryptographic operations and platform-specific functionality required by the library.

Available Ports
---------------

.. autosummary::
   :nosignatures:

   tropicsquare.ports.cpython.TropicSquareCPython
   tropicsquare.ports.micropython.TropicSquareMicroPython

Platform Comparison
-------------------

**CPython Port**
  - Uses the ``cryptography`` library for crypto operations
  - Full Python standard library support
  - Ideal for development, testing, and desktop applications

**MicroPython Port**
  - Embedded cryptographic implementations
  - Optimized for resource-constrained environments
  - Supports ESP32 and other MicroPython boards

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 1

   cpython
   micropython
