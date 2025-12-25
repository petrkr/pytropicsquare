"""UAP Pairing Key configuration classes"""

from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField
from tropicsquare.config.constants import (
    UAP_PKEY_WRITE_SLOT_0_POS,
    UAP_PKEY_WRITE_SLOT_1_POS,
    UAP_PKEY_WRITE_SLOT_2_POS,
    UAP_PKEY_WRITE_SLOT_3_POS,
    UAP_PKEY_READ_SLOT_0_POS,
    UAP_PKEY_READ_SLOT_1_POS,
    UAP_PKEY_READ_SLOT_2_POS,
    UAP_PKEY_READ_SLOT_3_POS,
    UAP_PKEY_INVALIDATE_SLOT_0_POS,
    UAP_PKEY_INVALIDATE_SLOT_1_POS,
    UAP_PKEY_INVALIDATE_SLOT_2_POS,
    UAP_PKEY_INVALIDATE_SLOT_3_POS
)


class PairingKeyWriteConfig(UapMultiSlotConfig):
    """UAP Pairing Key Write configuration (CFG_UAP_PAIRING_KEY_WRITE @ 0x20).

    Controls which pairing key slots can write to each pairing key slot.
    Has 4 slots, each with 8-bit permission field.

    Fields:
        slot_0: Permission for writing to pairing key slot 0
        slot_1: Permission for writing to pairing key slot 1
        slot_2: Permission for writing to pairing key slot 2
        slot_3: Permission for writing to pairing key slot 3
    """

    @property
    def slot_0(self):
        """Permission field for pairing key slot 0 write."""
        return self._get_slot_field(UAP_PKEY_WRITE_SLOT_0_POS)

    @slot_0.setter
    def slot_0(self, field):
        self._set_slot_field(UAP_PKEY_WRITE_SLOT_0_POS, field)

    @property
    def slot_1(self):
        """Permission field for pairing key slot 1 write."""
        return self._get_slot_field(UAP_PKEY_WRITE_SLOT_1_POS)

    @slot_1.setter
    def slot_1(self, field):
        self._set_slot_field(UAP_PKEY_WRITE_SLOT_1_POS, field)

    @property
    def slot_2(self):
        """Permission field for pairing key slot 2 write."""
        return self._get_slot_field(UAP_PKEY_WRITE_SLOT_2_POS)

    @slot_2.setter
    def slot_2(self, field):
        self._set_slot_field(UAP_PKEY_WRITE_SLOT_2_POS, field)

    @property
    def slot_3(self):
        """Permission field for pairing key slot 3 write."""
        return self._get_slot_field(UAP_PKEY_WRITE_SLOT_3_POS)

    @slot_3.setter
    def slot_3(self, field):
        self._set_slot_field(UAP_PKEY_WRITE_SLOT_3_POS, field)

    def to_dict(self):
        """Export fields as dictionary."""
        return {
            'slot_0': self.slot_0.to_dict(),
            'slot_1': self.slot_1.to_dict(),
            'slot_2': self.slot_2.to_dict(),
            'slot_3': self.slot_3.to_dict()
        }

    def __str__(self):
        """Human-readable representation."""
        return "PairingKeyWriteConfig(slot_0={}, slot_1={}, slot_2={}, slot_3={})".format(
            self.slot_0, self.slot_1, self.slot_2, self.slot_3)


class PairingKeyReadConfig(UapMultiSlotConfig):
    """UAP Pairing Key Read configuration (CFG_UAP_PAIRING_KEY_READ @ 0x24).

    Controls which pairing key slots can read from each pairing key slot.
    """

    @property
    def slot_0(self):
        """Permission field for pairing key slot 0 read."""
        return self._get_slot_field(UAP_PKEY_READ_SLOT_0_POS)

    @slot_0.setter
    def slot_0(self, field):
        self._set_slot_field(UAP_PKEY_READ_SLOT_0_POS, field)

    @property
    def slot_1(self):
        """Permission field for pairing key slot 1 read."""
        return self._get_slot_field(UAP_PKEY_READ_SLOT_1_POS)

    @slot_1.setter
    def slot_1(self, field):
        self._set_slot_field(UAP_PKEY_READ_SLOT_1_POS, field)

    @property
    def slot_2(self):
        """Permission field for pairing key slot 2 read."""
        return self._get_slot_field(UAP_PKEY_READ_SLOT_2_POS)

    @slot_2.setter
    def slot_2(self, field):
        self._set_slot_field(UAP_PKEY_READ_SLOT_2_POS, field)

    @property
    def slot_3(self):
        """Permission field for pairing key slot 3 read."""
        return self._get_slot_field(UAP_PKEY_READ_SLOT_3_POS)

    @slot_3.setter
    def slot_3(self, field):
        self._set_slot_field(UAP_PKEY_READ_SLOT_3_POS, field)

    def to_dict(self):
        """Export fields as dictionary."""
        return {
            'slot_0': self.slot_0.to_dict(),
            'slot_1': self.slot_1.to_dict(),
            'slot_2': self.slot_2.to_dict(),
            'slot_3': self.slot_3.to_dict()
        }

    def __str__(self):
        """Human-readable representation."""
        return "PairingKeyReadConfig(slot_0={}, slot_1={}, slot_2={}, slot_3={})".format(
            self.slot_0, self.slot_1, self.slot_2, self.slot_3)


class PairingKeyInvalidateConfig(UapMultiSlotConfig):
    """UAP Pairing Key Invalidate configuration (CFG_UAP_PAIRING_KEY_INVALIDATE @ 0x28).

    Controls which pairing key slots can invalidate each pairing key slot.
    """

    @property
    def slot_0(self):
        """Permission field for pairing key slot 0 invalidate."""
        return self._get_slot_field(UAP_PKEY_INVALIDATE_SLOT_0_POS)

    @slot_0.setter
    def slot_0(self, field):
        self._set_slot_field(UAP_PKEY_INVALIDATE_SLOT_0_POS, field)

    @property
    def slot_1(self):
        """Permission field for pairing key slot 1 invalidate."""
        return self._get_slot_field(UAP_PKEY_INVALIDATE_SLOT_1_POS)

    @slot_1.setter
    def slot_1(self, field):
        self._set_slot_field(UAP_PKEY_INVALIDATE_SLOT_1_POS, field)

    @property
    def slot_2(self):
        """Permission field for pairing key slot 2 invalidate."""
        return self._get_slot_field(UAP_PKEY_INVALIDATE_SLOT_2_POS)

    @slot_2.setter
    def slot_2(self, field):
        self._set_slot_field(UAP_PKEY_INVALIDATE_SLOT_2_POS, field)

    @property
    def slot_3(self):
        """Permission field for pairing key slot 3 invalidate."""
        return self._get_slot_field(UAP_PKEY_INVALIDATE_SLOT_3_POS)

    @slot_3.setter
    def slot_3(self, field):
        self._set_slot_field(UAP_PKEY_INVALIDATE_SLOT_3_POS, field)

    def to_dict(self):
        """Export fields as dictionary."""
        return {
            'slot_0': self.slot_0.to_dict(),
            'slot_1': self.slot_1.to_dict(),
            'slot_2': self.slot_2.to_dict(),
            'slot_3': self.slot_3.to_dict()
        }

    def __str__(self):
        """Human-readable representation."""
        return "PairingKeyInvalidateConfig(slot_0={}, slot_1={}, slot_2={}, slot_3={})".format(
            self.slot_0, self.slot_1, self.slot_2, self.slot_3)
