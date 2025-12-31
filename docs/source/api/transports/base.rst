L1Transport Base Class
======================

The base class for all L1 transport layer implementations. Platform-specific transports
inherit from this class and implement the abstract low-level methods.

.. currentmodule:: tropicsquare.transports

.. autoclass:: L1Transport
   :members:
   :undoc-members:
   :show-inheritance:

Abstract Methods
----------------

Subclasses must implement these methods:

* :meth:`~L1Transport._transfer` - Bidirectional SPI transfer
* :meth:`~L1Transport._read` - SPI read operation
* :meth:`~L1Transport._cs_low` - Activate chip select (optional)
* :meth:`~L1Transport._cs_high` - Deactivate chip select (optional)

Implemented Methods
-------------------

The base class provides:

* :meth:`~L1Transport.send_request` - Send request to chip
* :meth:`~L1Transport.get_response` - Get response with retry logic

See Also
--------

* :doc:`spi` - SPI transport implementation
* :doc:`uart` - UART transport implementation
* :doc:`network` - Network-SPI transport
* :doc:`tcp` - TCP transport for model server
* :doc:`/api/protocol` - L2 protocol using L1Transport
