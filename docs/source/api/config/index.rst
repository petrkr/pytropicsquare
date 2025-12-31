Configuration Management
========================

PyTropicSquare provides comprehensive configuration management for the TROPIC01 chip.
This includes startup configuration, system settings, and User Access Policy (UAP) management.

Configuration Types
-------------------

The TROPIC01 chip supports two types of configuration:

* **R-CONFIG** (Resettable Configuration) - Can be modified at runtime
* **I-CONFIG** (Immutable Configuration) - Set during manufacturing, read-only

Configuration Classes
---------------------

.. autosummary::
   :nosignatures:

   tropicsquare.config.base.BaseConfig
   tropicsquare.config.startup.StartUpConfig
   tropicsquare.config.sensors.SensorsConfig
   tropicsquare.config.debug.DebugConfig
   tropicsquare.config.gpo.GpoConfig
   tropicsquare.config.sleep_mode.SleepModeConfig

User Access Policy (UAP)
------------------------

The UAP system controls access permissions for chip resources, including memory slots,
operations, ECC key slots, and configuration access.

.. toctree::
   :maxdepth: 2

   base
   system
   uap/index

See Also
--------

* :doc:`/api/constants/index` - Configuration-related constants
