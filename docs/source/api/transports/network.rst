Network-SPI Transport
=====================

The Network-SPI transport enables communication with remote TROPIC01 chips via network connection.
This transport tunnels SPI communication over a network socket.

.. currentmodule:: tropicsquare.transports.network

.. automodule:: tropicsquare.transports.network
   :members:
   :undoc-members:
   :show-inheritance:

Use Cases
---------

* Remote chip access over WiFi
* Multi-device chip sharing
* Cloud-based chip services

Platform Support
----------------

* **MicroPython ESP32**: Full support with WiFi
* **CPython**: Supported (requires network access)

See Also
--------

* :doc:`spi` - Local SPI transport
* :doc:`tcp` - TCP transport for model server
