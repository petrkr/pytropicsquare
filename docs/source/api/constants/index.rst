Constants and Enumerations
===========================

This section documents all constants and enumerations used throughout PyTropicSquare,
including protocol constants, status codes, and configuration values.

Constant Categories
-------------------

.. autosummary::
   :nosignatures:

   tropicsquare.constants.l1
   tropicsquare.constants.l2
   tropicsquare.constants.chip_status
   tropicsquare.constants.rsp_status
   tropicsquare.constants.cmd_result
   tropicsquare.constants.ecc
   tropicsquare.constants.get_info_req
   tropicsquare.constants.pairing_keys

Usage
-----

Constants are typically accessed directly from their respective modules:

.. code-block:: python

   from tropicsquare.constants import chip_status, cmd_result

   if status == chip_status.ChipStatus.READY:
       print("Chip is ready")

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 1

   protocol
   status
   ecc
   info
   pairing_keys
