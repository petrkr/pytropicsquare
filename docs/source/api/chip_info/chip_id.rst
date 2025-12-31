Chip ID
=======

The ChipId class parses and provides access to chip identification information from the TROPIC01 secure element.

.. currentmodule:: tropicsquare.chip_id

.. autoclass:: ChipId
   :members:
   :undoc-members:
   :show-inheritance:

Chip ID Structure
-----------------

The chip ID contains:

* **Serial number** - Unique chip identifier
* **Hardware revision** - Chip hardware version
* **Firmware version** - Chip firmware version
* **Manufacturing data** - Additional manufacturing information

See Also
--------

* :doc:`serial_number` - Serial number utilities
* :doc:`/api/core` - TropicSquare.get_info_chip_id() method
