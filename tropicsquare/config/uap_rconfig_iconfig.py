"""UAP R-CONFIG and I-CONFIG configuration classes"""

from tropicsquare.config.uap_base import UapSingleFieldConfig, UapDualFieldConfig


class RConfigWriteEraseConfig(UapSingleFieldConfig):
    """UAP R-CONFIG Write/Erase configuration (CFG_UAP_R_CONFIG_WRITE_ERASE @ 0x30).

    Controls which pairing key slots can write or erase R-CONFIG.
    Single 8-bit permission field.
    """


class RConfigReadConfig(UapDualFieldConfig):
    """UAP R-CONFIG Read configuration (CFG_UAP_R_CONFIG_READ @ 0x34).

    Controls which pairing key slots can read R-CONFIG.
    Two 8-bit permission fields: CFG and FUNC.
    """


class IConfigWriteConfig(UapDualFieldConfig):
    """UAP I-CONFIG Write configuration (CFG_UAP_I_CONFIG_WRITE @ 0x40).

    Controls which pairing key slots can write I-CONFIG.
    Two 8-bit permission fields: CFG and FUNC.
    """


class IConfigReadConfig(UapDualFieldConfig):
    """UAP I-CONFIG Read configuration (CFG_UAP_I_CONFIG_READ @ 0x44).

    Controls which pairing key slots can read I-CONFIG.
    Two 8-bit permission fields: CFG and FUNC.
    """
