"""UAP ECC Key operation configuration classes"""

from tropicsquare.config.uap_base import UapDualFieldConfig


class EccKeyGenerateConfig(UapDualFieldConfig):
    """UAP ECC Key Generate configuration (CFG_UAP_ECC_KEY_GENERATE @ 0x130).

        Controls which pairing key slots can generate ECC keys.
        Two 8-bit permission fields: CFG and FUNC.
    """


class EccKeyStoreConfig(UapDualFieldConfig):
    """UAP ECC Key Store configuration (CFG_UAP_ECC_KEY_STORE @ 0x134).

        Controls which pairing key slots can store ECC keys.
        Two 8-bit permission fields: CFG and FUNC.
    """


class EccKeyReadConfig(UapDualFieldConfig):
    """UAP ECC Key Read configuration (CFG_UAP_ECC_KEY_READ @ 0x138).

        Controls which pairing key slots can read ECC keys.
        Two 8-bit permission fields: CFG and FUNC.
    """


class EccKeyEraseConfig(UapDualFieldConfig):
    """UAP ECC Key Erase configuration (CFG_UAP_ECC_KEY_ERASE @ 0x13C).

        Controls which pairing key slots can erase ECC keys.
        Two 8-bit permission fields: CFG and FUNC.
    """


class EcdsaSignConfig(UapDualFieldConfig):
    """UAP ECDSA Sign configuration (CFG_UAP_ECDSA_SIGN @ 0x140).

        Controls which pairing key slots can perform ECDSA signing.
        Two 8-bit permission fields: CFG and FUNC.
    """


class EddsaSignConfig(UapDualFieldConfig):
    """UAP EdDSA Sign configuration (CFG_UAP_EDDSA_SIGN @ 0x144).

        Controls which pairing key slots can perform EdDSA signing.
        Two 8-bit permission fields: CFG and FUNC.
    """
