TropicSquare Core Class
=======================

The :class:`~tropicsquare.TropicSquare` class is the main interface for communicating with the TROPIC01 secure element chip.
It implements the L2 and L3 protocol layers and provides high-level methods for all chip operations.

.. currentmodule:: tropicsquare

.. autoclass:: TropicSquare
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Platform-Specific Implementations
----------------------------------

For actual usage, you should use one of the platform-specific implementations:

* :class:`~tropicsquare.ports.cpython.TropicSquareCPython` - For CPython (development, desktop)
* :class:`~tropicsquare.ports.micropython.TropicSquareMicroPython` - For MicroPython (ESP32, embedded)

See Also
--------

* :doc:`protocol` - L2 protocol implementation details
* :doc:`ports/index` - Platform-specific implementations
* :doc:`transports/index` - Available transport layers
