"""UAP R-CONFIG and I-CONFIG configuration classes"""

from tropicsquare.config.uap_base import UapSingleFieldConfig, UapDualFieldConfig


class RConfigWriteEraseConfig(UapSingleFieldConfig):
    """UAP R-CONFIG Write/Erase configuration (CFG_UAP_R_CONFIG_WRITE_ERASE @ 0x30).

    Controls which pairing key slots can write or erase R-CONFIG.
    Single 8-bit permission field.
    """

    def __str__(self) -> str:
        """Human-readable representation."""
        return "RConfigWriteEraseConfig(permissions={})".format(self.permissions)


class RConfigReadConfig(UapDualFieldConfig):
    """UAP R-CONFIG Read configuration (CFG_UAP_R_CONFIG_READ @ 0x34).

    Controls which pairing key slots can read R-CONFIG.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self) -> str:
        """Human-readable representation."""
        return "RConfigReadConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class IConfigWriteConfig(UapDualFieldConfig):
    """UAP I-CONFIG Write configuration (CFG_UAP_I_CONFIG_WRITE @ 0x40).

    Controls which pairing key slots can write I-CONFIG.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self) -> str:
        """Human-readable representation."""
        return "IConfigWriteConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class IConfigReadConfig(UapDualFieldConfig):
    """UAP I-CONFIG Read configuration (CFG_UAP_I_CONFIG_READ @ 0x44).

    Controls which pairing key slots can read I-CONFIG.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self) -> str:
        """Human-readable representation."""
        return "IConfigReadConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)
