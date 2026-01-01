"""UAP Monotonic Counter operation configuration classes"""

from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField
from tropicsquare.config.constants import (
    UAP_MCOUNTER_0_3_POS,
    UAP_MCOUNTER_4_7_POS,
    UAP_MCOUNTER_8_11_POS,
    UAP_MCOUNTER_12_15_POS
)


class MCounterInitConfig(UapMultiSlotConfig):
    """UAP Monotonic Counter Init configuration (CFG_UAP_MCOUNTER_INIT @ 0x150).

    Controls which pairing key slots can initialize monotonic counters.
    Has 4 permission fields for counter groups 0-3, 4-7, 8-11, 12-15.
    """

    @property
    def mcounter_0_3(self) -> UapPermissionField:
        """Permission field for monotonic counters 0-3."""
        return self._get_slot_field(UAP_MCOUNTER_0_3_POS)

    @mcounter_0_3.setter
    def mcounter_0_3(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_0_3_POS, field)

    @property
    def mcounter_4_7(self) -> UapPermissionField:
        """Permission field for monotonic counters 4-7."""
        return self._get_slot_field(UAP_MCOUNTER_4_7_POS)

    @mcounter_4_7.setter
    def mcounter_4_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_4_7_POS, field)

    @property
    def mcounter_8_11(self) -> UapPermissionField:
        """Permission field for monotonic counters 8-11."""
        return self._get_slot_field(UAP_MCOUNTER_8_11_POS)

    @mcounter_8_11.setter
    def mcounter_8_11(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_8_11_POS, field)

    @property
    def mcounter_12_15(self) -> UapPermissionField:
        """Permission field for monotonic counters 12-15."""
        return self._get_slot_field(UAP_MCOUNTER_12_15_POS)

    @mcounter_12_15.setter
    def mcounter_12_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_12_15_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'mcounter_0_3': self.mcounter_0_3.to_dict(),
            'mcounter_4_7': self.mcounter_4_7.to_dict(),
            'mcounter_8_11': self.mcounter_8_11.to_dict(),
            'mcounter_12_15': self.mcounter_12_15.to_dict()
        }

    def __str__(self) -> str:
        """Table row with monotonic counter specific field names."""
        s0 = str(self.mcounter_0_3)
        s1 = str(self.mcounter_4_7)
        s2 = str(self.mcounter_8_11)
        s3 = str(self.mcounter_12_15)
        return "{:24s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class MCounterGetConfig(UapMultiSlotConfig):
    """UAP Monotonic Counter Get configuration (CFG_UAP_MCOUNTER_GET @ 0x154).

    Controls which pairing key slots can read monotonic counter values.
    Has 4 permission fields for counter groups 0-3, 4-7, 8-11, 12-15.
    """

    @property
    def mcounter_0_3(self) -> UapPermissionField:
        """Permission field for monotonic counters 0-3."""
        return self._get_slot_field(UAP_MCOUNTER_0_3_POS)

    @mcounter_0_3.setter
    def mcounter_0_3(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_0_3_POS, field)

    @property
    def mcounter_4_7(self) -> UapPermissionField:
        """Permission field for monotonic counters 4-7."""
        return self._get_slot_field(UAP_MCOUNTER_4_7_POS)

    @mcounter_4_7.setter
    def mcounter_4_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_4_7_POS, field)

    @property
    def mcounter_8_11(self) -> UapPermissionField:
        """Permission field for monotonic counters 8-11."""
        return self._get_slot_field(UAP_MCOUNTER_8_11_POS)

    @mcounter_8_11.setter
    def mcounter_8_11(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_8_11_POS, field)

    @property
    def mcounter_12_15(self) -> UapPermissionField:
        """Permission field for monotonic counters 12-15."""
        return self._get_slot_field(UAP_MCOUNTER_12_15_POS)

    @mcounter_12_15.setter
    def mcounter_12_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_12_15_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'mcounter_0_3': self.mcounter_0_3.to_dict(),
            'mcounter_4_7': self.mcounter_4_7.to_dict(),
            'mcounter_8_11': self.mcounter_8_11.to_dict(),
            'mcounter_12_15': self.mcounter_12_15.to_dict()
        }

    def __str__(self) -> str:
        """Table row with monotonic counter specific field names."""
        s0 = str(self.mcounter_0_3)
        s1 = str(self.mcounter_4_7)
        s2 = str(self.mcounter_8_11)
        s3 = str(self.mcounter_12_15)
        return "{:24s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class MCounterUpdateConfig(UapMultiSlotConfig):
    """UAP Monotonic Counter Update configuration (CFG_UAP_MCOUNTER_UPDATE @ 0x158).

    Controls which pairing key slots can update monotonic counters.
    Has 4 permission fields for counter groups 0-3, 4-7, 8-11, 12-15.
    """

    @property
    def mcounter_0_3(self) -> UapPermissionField:
        """Permission field for monotonic counters 0-3."""
        return self._get_slot_field(UAP_MCOUNTER_0_3_POS)

    @mcounter_0_3.setter
    def mcounter_0_3(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_0_3_POS, field)

    @property
    def mcounter_4_7(self) -> UapPermissionField:
        """Permission field for monotonic counters 4-7."""
        return self._get_slot_field(UAP_MCOUNTER_4_7_POS)

    @mcounter_4_7.setter
    def mcounter_4_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_4_7_POS, field)

    @property
    def mcounter_8_11(self) -> UapPermissionField:
        """Permission field for monotonic counters 8-11."""
        return self._get_slot_field(UAP_MCOUNTER_8_11_POS)

    @mcounter_8_11.setter
    def mcounter_8_11(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_8_11_POS, field)

    @property
    def mcounter_12_15(self) -> UapPermissionField:
        """Permission field for monotonic counters 12-15."""
        return self._get_slot_field(UAP_MCOUNTER_12_15_POS)

    @mcounter_12_15.setter
    def mcounter_12_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_MCOUNTER_12_15_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'mcounter_0_3': self.mcounter_0_3.to_dict(),
            'mcounter_4_7': self.mcounter_4_7.to_dict(),
            'mcounter_8_11': self.mcounter_8_11.to_dict(),
            'mcounter_12_15': self.mcounter_12_15.to_dict()
        }

    def __str__(self) -> str:
        """Table row with monotonic counter specific field names."""
        s0 = str(self.mcounter_0_3)
        s1 = str(self.mcounter_4_7)
        s2 = str(self.mcounter_8_11)
        s3 = str(self.mcounter_12_15)
        return "{:24s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )
