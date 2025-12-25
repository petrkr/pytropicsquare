"""UAP Operation configuration classes

These classes control permissions for various TROPIC01 operations.
"""

from tropicsquare.config.uap_base import UapSingleFieldConfig, UapDualFieldConfig


class PingConfig(UapDualFieldConfig):
    """UAP PING configuration (CFG_UAP_PING @ 0x100).

    Controls which pairing key slots can execute PING command.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "PingConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class RandomValueGetConfig(UapDualFieldConfig):
    """UAP Random Value Get configuration (CFG_UAP_RANDOM_VALUE_GET @ 0x120).

    Controls which pairing key slots can get random values.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "RandomValueGetConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)


class MacAndDestroyConfig(UapDualFieldConfig):
    """UAP MAC and Destroy configuration (CFG_UAP_MAC_AND_DESTROY @ 0x160).

    Controls which pairing key slots can execute MAC and destroy operations.
    Two 8-bit permission fields: CFG and FUNC.
    """

    def __str__(self):
        """Human-readable representation."""
        return "MacAndDestroyConfig(cfg={}, func={})".format(
            self.cfg_permissions, self.func_permissions)
