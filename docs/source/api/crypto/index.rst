Cryptographic Operations
========================

This module provides cryptographic operation support for the TROPIC01 chip,
including ECC (Elliptic Curve Cryptography) operations and signature handling.

ECC Support
-----------

The TROPIC01 chip supports two elliptic curve types:

* **P-256** (NIST P-256 / secp256r1) - ECDSA signatures
* **Ed25519** - EdDSA signatures

Available Classes
-----------------

.. autosummary::
   :nosignatures:

   tropicsquare.ecc.EccKeyInfo
   tropicsquare.ecc.signature.EcdsaSignature
   tropicsquare.ecc.signature.EddsaSignature

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 1

   ecc
   signatures

See Also
--------

* :doc:`/api/constants/ecc` - ECC-related constants
* :doc:`/api/config/uap/crypto` - ECC access control via UAP
