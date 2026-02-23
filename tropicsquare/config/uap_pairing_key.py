"""UAP Pairing Key configuration classes"""

from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField
from tropicsquare.config.constants import (
    UAP_PKEY_SLOT_0_POS,
    UAP_PKEY_SLOT_1_POS,
    UAP_PKEY_SLOT_2_POS,
    UAP_PKEY_SLOT_3_POS
)


class PairingKeyConfig(UapMultiSlotConfig):
    """UAP Pairing Key base configuration"""

    @property
    def pkey_slot_0(self) -> UapPermissionField:
        """Permission field for pairing key slot 0 write."""
        return self._get_slot_field(UAP_PKEY_SLOT_0_POS)

    @pkey_slot_0.setter
    def pkey_slot_0(self, field) -> None:
        self._set_slot_field(UAP_PKEY_SLOT_0_POS, field)

    @property
    def pkey_slot_1(self) -> UapPermissionField:
        """Permission field for pairing key slot 1 write."""
        return self._get_slot_field(UAP_PKEY_SLOT_1_POS)

    @pkey_slot_1.setter
    def pkey_slot_1(self, field) -> None:
        self._set_slot_field(UAP_PKEY_SLOT_1_POS, field)

    @property
    def pkey_slot_2(self) -> UapPermissionField:
        """Permission field for pairing key slot 2 write."""
        return self._get_slot_field(UAP_PKEY_SLOT_2_POS)

    @pkey_slot_2.setter
    def pkey_slot_2(self, field) -> None:
        self._set_slot_field(UAP_PKEY_SLOT_2_POS, field)

    @property
    def pkey_slot_3(self) -> UapPermissionField:
        """Permission field for pairing key slot 3 write."""
        return self._get_slot_field(UAP_PKEY_SLOT_3_POS)

    @pkey_slot_3.setter
    def pkey_slot_3(self, field) -> None:
        self._set_slot_field(UAP_PKEY_SLOT_3_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'pkey_slot_0': self.pkey_slot_0.to_dict(),
            'pkey_slot_1': self.pkey_slot_1.to_dict(),
            'pkey_slot_2': self.pkey_slot_2.to_dict(),
            'pkey_slot_3': self.pkey_slot_3.to_dict()
        }

    def __str__(self) -> str:
        """Table row with pairing key slot specific field names."""
        s0 = str(self.pkey_slot_0)
        s1 = str(self.pkey_slot_1)
        s2 = str(self.pkey_slot_2)
        s3 = str(self.pkey_slot_3)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class PairingKeyWriteConfig(PairingKeyConfig):
    """UAP Pairing Key Write configuration (CFG_UAP_PAIRING_KEY_WRITE @ 0x20).

        Controls which pairing key slots can write to each pairing key slot.
        Has 4 slots, each with 8-bit permission field.
    """


class PairingKeyReadConfig(PairingKeyConfig):
    """UAP Pairing Key Read configuration (CFG_UAP_PAIRING_KEY_READ @ 0x24).

       Controls which pairing key slots can read from each pairing key slot.
    """


class PairingKeyInvalidateConfig(PairingKeyConfig):
    """UAP Pairing Key Invalidate configuration (CFG_UAP_PAIRING_KEY_INVALIDATE @ 0x28).

    Controls which pairing key slots can invalidate each pairing key slot.
    """
