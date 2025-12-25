"""UAP Monotonic Counter operation configuration classes"""

from tropicsquare.config.uap_base import UapDualFieldConfig


class MCounterInitConfig(UapDualFieldConfig):
    """UAP Monotonic Counter Init configuration (CFG_UAP_MCOUNTER_INIT @ 0x150).

    Controls which pairing key slots can initialize monotonic counters.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "MCounterInitConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class MCounterGetConfig(UapDualFieldConfig):
    """UAP Monotonic Counter Get configuration (CFG_UAP_MCOUNTER_GET @ 0x154).

    Controls which pairing key slots can read monotonic counter values.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "MCounterGetConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class MCounterUpdateConfig(UapDualFieldConfig):
    """UAP Monotonic Counter Update configuration (CFG_UAP_MCOUNTER_UPDATE @ 0x158).

    Controls which pairing key slots can update monotonic counters.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "MCounterUpdateConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)
