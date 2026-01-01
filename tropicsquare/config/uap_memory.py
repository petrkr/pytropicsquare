"""UAP Memory operation configuration classes"""

from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField
from tropicsquare.config.constants import (
    UAP_UDATA_SLOT_0_127_POS,
    UAP_UDATA_SLOT_128_255_POS,
    UAP_UDATA_SLOT_256_383_POS,
    UAP_UDATA_SLOT_384_511_POS
)


class RMemDataWriteConfig(UapMultiSlotConfig):
    """UAP R-MEM Data Write configuration (CFG_UAP_R_MEM_DATA_WRITE @ 0x110).

    Controls which pairing key slots can write to R-MEM User Data slots.
    Has 4 permission fields for slot ranges 0-127, 128-255, 256-383, 384-511.
    """

    @property
    def udata_slot_0_127(self) -> UapPermissionField:
        """Permission field for User Data slots 0-127."""
        return self._get_slot_field(UAP_UDATA_SLOT_0_127_POS)

    @udata_slot_0_127.setter
    def udata_slot_0_127(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_0_127_POS, field)

    @property
    def udata_slot_128_255(self) -> UapPermissionField:
        """Permission field for User Data slots 128-255."""
        return self._get_slot_field(UAP_UDATA_SLOT_128_255_POS)

    @udata_slot_128_255.setter
    def udata_slot_128_255(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_128_255_POS, field)

    @property
    def udata_slot_256_383(self) -> UapPermissionField:
        """Permission field for User Data slots 256-383."""
        return self._get_slot_field(UAP_UDATA_SLOT_256_383_POS)

    @udata_slot_256_383.setter
    def udata_slot_256_383(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_256_383_POS, field)

    @property
    def udata_slot_384_511(self) -> UapPermissionField:
        """Permission field for User Data slots 384-511."""
        return self._get_slot_field(UAP_UDATA_SLOT_384_511_POS)

    @udata_slot_384_511.setter
    def udata_slot_384_511(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_384_511_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'udata_slot_0_127': self.udata_slot_0_127.to_dict(),
            'udata_slot_128_255': self.udata_slot_128_255.to_dict(),
            'udata_slot_256_383': self.udata_slot_256_383.to_dict(),
            'udata_slot_384_511': self.udata_slot_384_511.to_dict()
        }

    def __str__(self) -> str:
        """Table row with User Data slot specific field names."""
        s0 = str(self.udata_slot_0_127)
        s1 = str(self.udata_slot_128_255)
        s2 = str(self.udata_slot_256_383)
        s3 = str(self.udata_slot_384_511)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class RMemDataReadConfig(UapMultiSlotConfig):
    """UAP R-MEM Data Read configuration (CFG_UAP_R_MEM_DATA_READ @ 0x114).

    Controls which pairing key slots can read from R-MEM User Data slots.
    Has 4 permission fields for slot ranges 0-127, 128-255, 256-383, 384-511.
    """

    @property
    def udata_slot_0_127(self) -> UapPermissionField:
        """Permission field for User Data slots 0-127."""
        return self._get_slot_field(UAP_UDATA_SLOT_0_127_POS)

    @udata_slot_0_127.setter
    def udata_slot_0_127(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_0_127_POS, field)

    @property
    def udata_slot_128_255(self) -> UapPermissionField:
        """Permission field for User Data slots 128-255."""
        return self._get_slot_field(UAP_UDATA_SLOT_128_255_POS)

    @udata_slot_128_255.setter
    def udata_slot_128_255(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_128_255_POS, field)

    @property
    def udata_slot_256_383(self) -> UapPermissionField:
        """Permission field for User Data slots 256-383."""
        return self._get_slot_field(UAP_UDATA_SLOT_256_383_POS)

    @udata_slot_256_383.setter
    def udata_slot_256_383(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_256_383_POS, field)

    @property
    def udata_slot_384_511(self) -> UapPermissionField:
        """Permission field for User Data slots 384-511."""
        return self._get_slot_field(UAP_UDATA_SLOT_384_511_POS)

    @udata_slot_384_511.setter
    def udata_slot_384_511(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_384_511_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'udata_slot_0_127': self.udata_slot_0_127.to_dict(),
            'udata_slot_128_255': self.udata_slot_128_255.to_dict(),
            'udata_slot_256_383': self.udata_slot_256_383.to_dict(),
            'udata_slot_384_511': self.udata_slot_384_511.to_dict()
        }

    def __str__(self) -> str:
        """Table row with User Data slot specific field names."""
        s0 = str(self.udata_slot_0_127)
        s1 = str(self.udata_slot_128_255)
        s2 = str(self.udata_slot_256_383)
        s3 = str(self.udata_slot_384_511)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class RMemDataEraseConfig(UapMultiSlotConfig):
    """UAP R-MEM Data Erase configuration (CFG_UAP_R_MEM_DATA_ERASE @ 0x118).

    Controls which pairing key slots can erase R-MEM User Data slots.
    Has 4 permission fields for slot ranges 0-127, 128-255, 256-383, 384-511.
    """

    @property
    def udata_slot_0_127(self) -> UapPermissionField:
        """Permission field for User Data slots 0-127."""
        return self._get_slot_field(UAP_UDATA_SLOT_0_127_POS)

    @udata_slot_0_127.setter
    def udata_slot_0_127(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_0_127_POS, field)

    @property
    def udata_slot_128_255(self) -> UapPermissionField:
        """Permission field for User Data slots 128-255."""
        return self._get_slot_field(UAP_UDATA_SLOT_128_255_POS)

    @udata_slot_128_255.setter
    def udata_slot_128_255(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_128_255_POS, field)

    @property
    def udata_slot_256_383(self) -> UapPermissionField:
        """Permission field for User Data slots 256-383."""
        return self._get_slot_field(UAP_UDATA_SLOT_256_383_POS)

    @udata_slot_256_383.setter
    def udata_slot_256_383(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_256_383_POS, field)

    @property
    def udata_slot_384_511(self) -> UapPermissionField:
        """Permission field for User Data slots 384-511."""
        return self._get_slot_field(UAP_UDATA_SLOT_384_511_POS)

    @udata_slot_384_511.setter
    def udata_slot_384_511(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_UDATA_SLOT_384_511_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'udata_slot_0_127': self.udata_slot_0_127.to_dict(),
            'udata_slot_128_255': self.udata_slot_128_255.to_dict(),
            'udata_slot_256_383': self.udata_slot_256_383.to_dict(),
            'udata_slot_384_511': self.udata_slot_384_511.to_dict()
        }

    def __str__(self) -> str:
        """Table row with User Data slot specific field names."""
        s0 = str(self.udata_slot_0_127)
        s1 = str(self.udata_slot_128_255)
        s2 = str(self.udata_slot_256_383)
        s3 = str(self.udata_slot_384_511)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )
