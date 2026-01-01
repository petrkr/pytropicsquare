"""UAP Operation configuration classes

These classes control permissions for various TROPIC01 operations.
"""

from tropicsquare.config.uap_base import UapSingleFieldConfig, UapMultiSlotConfig, UapPermissionField
from tropicsquare.config.constants import (
    UAP_MACANDD_0_31_POS,
    UAP_MACANDD_32_63_POS,
    UAP_MACANDD_64_95_POS,
    UAP_MACANDD_96_127_POS
)


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

    Controls access privileges to MAC-and-Destroy partition slots.
    Has 4 permission fields, each controlling access to a range of MAC-and-Destroy slots.
    """

    @property
    def macandadd0_31(self) -> UapPermissionField:
        """Permission field for MAC-and-Destroy slots 0-31."""
        return self._get_slot_field(UAP_MACANDD_0_31_POS)

    @macandadd0_31.setter
    def macandadd0_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MACANDD_0_31_POS, field)

    @property
    def macandadd32_63(self) -> UapPermissionField:
        """Permission field for MAC-and-Destroy slots 32-63."""
        return self._get_slot_field(UAP_MACANDD_32_63_POS)

    @macandadd32_63.setter
    def macandadd32_63(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MACANDD_32_63_POS, field)

    @property
    def macandadd64_95(self) -> UapPermissionField:
        """Permission field for MAC-and-Destroy slots 64-95."""
        return self._get_slot_field(UAP_MACANDD_64_95_POS)

    @macandadd64_95.setter
    def macandadd64_95(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MACANDD_64_95_POS, field)

    @property
    def macandadd96_127(self) -> UapPermissionField:
        """Permission field for MAC-and-Destroy slots 96-127."""
        return self._get_slot_field(UAP_MACANDD_96_127_POS)

    @macandadd96_127.setter
    def macandadd96_127(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MACANDD_96_127_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'macandadd0_31': self.macandadd0_31.to_dict(),
            'macandadd32_63': self.macandadd32_63.to_dict(),
            'macandadd64_95': self.macandadd64_95.to_dict(),
            'macandadd96_127': self.macandadd96_127.to_dict()
        }

    def __str__(self) -> str:
        """Table row with MAC-and-Destroy specific field names."""
        s0 = str(self.macandadd0_31)
        s1 = str(self.macandadd32_63)
        s2 = str(self.macandadd64_95)
        s3 = str(self.macandadd96_127)
        return "{:24s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )
