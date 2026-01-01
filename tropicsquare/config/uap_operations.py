"""UAP Operation configuration classes

These classes control permissions for various TROPIC01 operations.
"""

from tropicsquare.config.uap_base import UapSingleFieldConfig, UapMultiSlotConfig


class PingConfig(UapSingleFieldConfig):
    """UAP PING configuration (CFG_UA`P_PING @ 0x100).

    Controls which pairing key slots can execute PING command.
    Single 8-bit permission field.
    """


class RandomValueGetConfig(UapSingleFieldConfig):
    """UAP Random Value Get configuration (CFG_UAP_RANDOM_VALUE_GET @ 0x120).

    Controls which pairing key slots can get random values.
    Single 8-bit permission field.
    """


class MacAndDestroyConfig(UapMultiSlotConfig):
    """UAP MAC and Destroy configuration (CFG_UAP_MAC_AND_DESTROY @ 0x160).

    Controls which pairing key slots can execute MAC and destroy operations.
    Two 8-bit permission fields: CFG and FUNC.
    """
