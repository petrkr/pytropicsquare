API Reference
=============

This section provides detailed documentation of all PyTropicSquare classes, functions, and constants.

Overview
--------

PyTropicSquare provides a Python interface for communicating with Tropic Square TROPIC01 secure element chips.
The library is organized into several functional areas:

* **Core API** - Main :class:`~tropicsquare.TropicSquare` class for chip communication
* **Protocol Layer** - L2 protocol implementation for secure communication
* **Transports** - Multiple transport options (SPI, UART, Network, TCP)
* **Platform Ports** - CPython and MicroPython implementations
* **Configuration** - Chip configuration and User Access Policy (UAP) management
* **Chip Information** - Chip ID parsing and serial number utilities
* **Cryptographic Operations** - ECC operations and signature handling
* **Constants** - Protocol constants, status codes, and enumerations
* **Utilities** - CRC calculation, error mapping, and exception classes

Quick Reference
---------------

Main Classes
^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   tropicsquare.TropicSquare
   tropicsquare.ports.cpython.TropicSquareCPython
   tropicsquare.ports.micropython.TropicSquareMicroPython
   tropicsquare.l2_protocol.L2Protocol

Transport Classes
^^^^^^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   tropicsquare.transports.spi.SpiTransport
   tropicsquare.transports.uart.UartTransport
   tropicsquare.transports.network.NetworkSpiTransport
   tropicsquare.transports.tcp.TcpTransport

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 2

   core
   protocol
   transports/index
   ports/index
   chip_info/index
   config/index
   crypto/index
   constants/index
   utilities/index
