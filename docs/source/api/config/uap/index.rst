User Access Policy (UAP)
========================

The User Access Policy (UAP) system provides fine-grained access control for chip resources.
UAP settings control which operations are allowed and how chip resources can be accessed.

UAP Overview
------------

The UAP system manages access to:

* **Memory slots** - Data storage areas
* **Operations** - Chip operations and commands
* **Monotonic counters** - Counter resources
* **ECC key slots** - Cryptographic keys
* **Configuration access** - Pairing keys and config modification rights

UAP Classes
-----------

.. autosummary::
   :nosignatures:

   tropicsquare.config.uap_memory.RMemDataReadConfig
   tropicsquare.config.uap_memory.RMemDataWriteConfig
   tropicsquare.config.uap_memory.RMemDataEraseConfig
   tropicsquare.config.uap_operations.PingConfig
   tropicsquare.config.uap_operations.RandomValueGetConfig
   tropicsquare.config.uap_operations.MacAndDestroyConfig
   tropicsquare.config.uap_mcounter.MCounterInitConfig
   tropicsquare.config.uap_mcounter.MCounterUpdateConfig
   tropicsquare.config.uap_mcounter.MCounterGetConfig
   tropicsquare.config.uap_ecc.EccKeyGenerateConfig
   tropicsquare.config.uap_ecc.EccKeyStoreConfig
   tropicsquare.config.uap_ecc.EccKeyReadConfig
   tropicsquare.config.uap_ecc.EccKeyEraseConfig
   tropicsquare.config.uap_ecc.EcdsaSignConfig
   tropicsquare.config.uap_ecc.EddsaSignConfig
   tropicsquare.config.uap_pairing_key.PairingKeyWriteConfig
   tropicsquare.config.uap_pairing_key.PairingKeyReadConfig
   tropicsquare.config.uap_pairing_key.PairingKeyInvalidateConfig
   tropicsquare.config.uap_rconfig_iconfig.RConfigReadConfig
   tropicsquare.config.uap_rconfig_iconfig.RConfigWriteEraseConfig
   tropicsquare.config.uap_rconfig_iconfig.IConfigReadConfig
   tropicsquare.config.uap_rconfig_iconfig.IConfigWriteConfig

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 1

   base
   resources
   crypto
   access
