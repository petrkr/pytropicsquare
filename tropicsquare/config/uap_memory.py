"""UAP Memory operation configuration classes"""

from tropicsquare.config.uap_base import UapDualFieldConfig


class RMemDataWriteConfig(UapDualFieldConfig):
    """UAP R-MEM Data Write configuration (CFG_UAP_R_MEM_DATA_WRITE @ 0x110).

    Controls which pairing key slots can write to R-MEM data slots.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "RMemDataWriteConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class RMemDataReadConfig(UapDualFieldConfig):
    """UAP R-MEM Data Read configuration (CFG_UAP_R_MEM_DATA_READ @ 0x114).

    Controls which pairing key slots can read from R-MEM data slots.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "RMemDataReadConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class RMemDataEraseConfig(UapDualFieldConfig):
    """UAP R-MEM Data Erase configuration (CFG_UAP_R_MEM_DATA_ERASE @ 0x118).

    Controls which pairing key slots can erase R-MEM data slots.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "RMemDataEraseConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)
