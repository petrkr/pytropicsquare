L2 Protocol Layer
=================

The L2 protocol layer handles low-level communication with the TROPIC01 chip,
including CRC validation, encrypted sessions, and command/response framing.

.. currentmodule:: tropicsquare.l2_protocol

.. automodule:: tropicsquare.l2_protocol
   :members:
   :undoc-members:
   :show-inheritance:

Protocol Overview
-----------------

The L2 protocol provides:

* **CRC validation** - Data integrity checking
* **Encrypted sessions** - Secure communication using X25519 key exchange and AES-GCM
* **Command framing** - Proper command structure and response parsing
* **Status handling** - Chip status and error code processing

Session Management
------------------

Before executing L3 commands, a secure session must be established using the :meth:`~tropicsquare.TropicSquare.start_secure_session` method.

See Also
--------

* :doc:`core` - Main TropicSquare class using this protocol
* :doc:`transports/base` - L1Transport base class
* :doc:`utilities/crc` - CRC calculation utilities
* :doc:`constants/protocol` - L2 protocol constants
