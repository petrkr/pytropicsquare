"""UAP ECC Key operation configuration classes"""

from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField
from tropicsquare.config.constants import (
    UAP_ECCKEY_SLOT_0_7_POS,
    UAP_ECCKEY_SLOT_8_15_POS,
    UAP_ECCKEY_SLOT_16_23_POS,
    UAP_ECCKEY_SLOT_24_31_POS
)


class EccKeyGenerateConfig(UapMultiSlotConfig):
    """UAP ECC Key Generate configuration (CFG_UAP_ECC_KEY_GENERATE @ 0x130).

    Controls which pairing key slots can generate ECC keys.
    Has 4 permission fields for ECC Key slot groups 0-7, 8-15, 16-23, 24-31.
    """

    @property
    def ecckey_slot_0_7(self) -> UapPermissionField:
        """Permission field for ECC Key slots 0-7."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_0_7_POS)

    @ecckey_slot_0_7.setter
    def ecckey_slot_0_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_0_7_POS, field)

    @property
    def ecckey_slot_8_15(self) -> UapPermissionField:
        """Permission field for ECC Key slots 8-15."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_8_15_POS)

    @ecckey_slot_8_15.setter
    def ecckey_slot_8_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_8_15_POS, field)

    @property
    def ecckey_slot_16_23(self) -> UapPermissionField:
        """Permission field for ECC Key slots 16-23."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_16_23_POS)

    @ecckey_slot_16_23.setter
    def ecckey_slot_16_23(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_16_23_POS, field)

    @property
    def ecckey_slot_24_31(self) -> UapPermissionField:
        """Permission field for ECC Key slots 24-31."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_24_31_POS)

    @ecckey_slot_24_31.setter
    def ecckey_slot_24_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_24_31_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'ecckey_slot_0_7': self.ecckey_slot_0_7.to_dict(),
            'ecckey_slot_8_15': self.ecckey_slot_8_15.to_dict(),
            'ecckey_slot_16_23': self.ecckey_slot_16_23.to_dict(),
            'ecckey_slot_24_31': self.ecckey_slot_24_31.to_dict()
        }

    def __str__(self) -> str:
        """Table row with ECC Key slot specific field names."""
        s0 = str(self.ecckey_slot_0_7)
        s1 = str(self.ecckey_slot_8_15)
        s2 = str(self.ecckey_slot_16_23)
        s3 = str(self.ecckey_slot_24_31)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class EccKeyStoreConfig(UapMultiSlotConfig):
    """UAP ECC Key Store configuration (CFG_UAP_ECC_KEY_STORE @ 0x134).

    Controls which pairing key slots can store ECC keys.
    Has 4 permission fields for ECC Key slot groups 0-7, 8-15, 16-23, 24-31.
    """

    @property
    def ecckey_slot_0_7(self) -> UapPermissionField:
        """Permission field for ECC Key slots 0-7."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_0_7_POS)

    @ecckey_slot_0_7.setter
    def ecckey_slot_0_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_0_7_POS, field)

    @property
    def ecckey_slot_8_15(self) -> UapPermissionField:
        """Permission field for ECC Key slots 8-15."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_8_15_POS)

    @ecckey_slot_8_15.setter
    def ecckey_slot_8_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_8_15_POS, field)

    @property
    def ecckey_slot_16_23(self) -> UapPermissionField:
        """Permission field for ECC Key slots 16-23."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_16_23_POS)

    @ecckey_slot_16_23.setter
    def ecckey_slot_16_23(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_16_23_POS, field)

    @property
    def ecckey_slot_24_31(self) -> UapPermissionField:
        """Permission field for ECC Key slots 24-31."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_24_31_POS)

    @ecckey_slot_24_31.setter
    def ecckey_slot_24_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_24_31_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'ecckey_slot_0_7': self.ecckey_slot_0_7.to_dict(),
            'ecckey_slot_8_15': self.ecckey_slot_8_15.to_dict(),
            'ecckey_slot_16_23': self.ecckey_slot_16_23.to_dict(),
            'ecckey_slot_24_31': self.ecckey_slot_24_31.to_dict()
        }

    def __str__(self) -> str:
        """Table row with ECC Key slot specific field names."""
        s0 = str(self.ecckey_slot_0_7)
        s1 = str(self.ecckey_slot_8_15)
        s2 = str(self.ecckey_slot_16_23)
        s3 = str(self.ecckey_slot_24_31)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class EccKeyReadConfig(UapMultiSlotConfig):
    """UAP ECC Key Read configuration (CFG_UAP_ECC_KEY_READ @ 0x138).

    Controls which pairing key slots can read ECC keys.
    Has 4 permission fields for ECC Key slot groups 0-7, 8-15, 16-23, 24-31.
    """

    @property
    def ecckey_slot_0_7(self) -> UapPermissionField:
        """Permission field for ECC Key slots 0-7."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_0_7_POS)

    @ecckey_slot_0_7.setter
    def ecckey_slot_0_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_0_7_POS, field)

    @property
    def ecckey_slot_8_15(self) -> UapPermissionField:
        """Permission field for ECC Key slots 8-15."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_8_15_POS)

    @ecckey_slot_8_15.setter
    def ecckey_slot_8_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_8_15_POS, field)

    @property
    def ecckey_slot_16_23(self) -> UapPermissionField:
        """Permission field for ECC Key slots 16-23."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_16_23_POS)

    @ecckey_slot_16_23.setter
    def ecckey_slot_16_23(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_16_23_POS, field)

    @property
    def ecckey_slot_24_31(self) -> UapPermissionField:
        """Permission field for ECC Key slots 24-31."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_24_31_POS)

    @ecckey_slot_24_31.setter
    def ecckey_slot_24_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_24_31_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'ecckey_slot_0_7': self.ecckey_slot_0_7.to_dict(),
            'ecckey_slot_8_15': self.ecckey_slot_8_15.to_dict(),
            'ecckey_slot_16_23': self.ecckey_slot_16_23.to_dict(),
            'ecckey_slot_24_31': self.ecckey_slot_24_31.to_dict()
        }

    def __str__(self) -> str:
        """Table row with ECC Key slot specific field names."""
        s0 = str(self.ecckey_slot_0_7)
        s1 = str(self.ecckey_slot_8_15)
        s2 = str(self.ecckey_slot_16_23)
        s3 = str(self.ecckey_slot_24_31)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class EccKeyEraseConfig(UapMultiSlotConfig):
    """UAP ECC Key Erase configuration (CFG_UAP_ECC_KEY_ERASE @ 0x13C).

    Controls which pairing key slots can erase ECC keys.
    Has 4 permission fields for ECC Key slot groups 0-7, 8-15, 16-23, 24-31.
    """

    @property
    def ecckey_slot_0_7(self) -> UapPermissionField:
        """Permission field for ECC Key slots 0-7."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_0_7_POS)

    @ecckey_slot_0_7.setter
    def ecckey_slot_0_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_0_7_POS, field)

    @property
    def ecckey_slot_8_15(self) -> UapPermissionField:
        """Permission field for ECC Key slots 8-15."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_8_15_POS)

    @ecckey_slot_8_15.setter
    def ecckey_slot_8_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_8_15_POS, field)

    @property
    def ecckey_slot_16_23(self) -> UapPermissionField:
        """Permission field for ECC Key slots 16-23."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_16_23_POS)

    @ecckey_slot_16_23.setter
    def ecckey_slot_16_23(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_16_23_POS, field)

    @property
    def ecckey_slot_24_31(self) -> UapPermissionField:
        """Permission field for ECC Key slots 24-31."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_24_31_POS)

    @ecckey_slot_24_31.setter
    def ecckey_slot_24_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_24_31_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'ecckey_slot_0_7': self.ecckey_slot_0_7.to_dict(),
            'ecckey_slot_8_15': self.ecckey_slot_8_15.to_dict(),
            'ecckey_slot_16_23': self.ecckey_slot_16_23.to_dict(),
            'ecckey_slot_24_31': self.ecckey_slot_24_31.to_dict()
        }

    def __str__(self) -> str:
        """Table row with ECC Key slot specific field names."""
        s0 = str(self.ecckey_slot_0_7)
        s1 = str(self.ecckey_slot_8_15)
        s2 = str(self.ecckey_slot_16_23)
        s3 = str(self.ecckey_slot_24_31)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class EcdsaSignConfig(UapMultiSlotConfig):
    """UAP ECDSA Sign configuration (CFG_UAP_ECDSA_SIGN @ 0x140).

    Controls which pairing key slots can perform ECDSA signing.
    Has 4 permission fields for ECC Key slot groups 0-7, 8-15, 16-23, 24-31.
    """

    @property
    def ecckey_slot_0_7(self) -> UapPermissionField:
        """Permission field for ECC Key slots 0-7."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_0_7_POS)

    @ecckey_slot_0_7.setter
    def ecckey_slot_0_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_0_7_POS, field)

    @property
    def ecckey_slot_8_15(self) -> UapPermissionField:
        """Permission field for ECC Key slots 8-15."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_8_15_POS)

    @ecckey_slot_8_15.setter
    def ecckey_slot_8_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_8_15_POS, field)

    @property
    def ecckey_slot_16_23(self) -> UapPermissionField:
        """Permission field for ECC Key slots 16-23."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_16_23_POS)

    @ecckey_slot_16_23.setter
    def ecckey_slot_16_23(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_16_23_POS, field)

    @property
    def ecckey_slot_24_31(self) -> UapPermissionField:
        """Permission field for ECC Key slots 24-31."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_24_31_POS)

    @ecckey_slot_24_31.setter
    def ecckey_slot_24_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_24_31_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'ecckey_slot_0_7': self.ecckey_slot_0_7.to_dict(),
            'ecckey_slot_8_15': self.ecckey_slot_8_15.to_dict(),
            'ecckey_slot_16_23': self.ecckey_slot_16_23.to_dict(),
            'ecckey_slot_24_31': self.ecckey_slot_24_31.to_dict()
        }

    def __str__(self) -> str:
        """Table row with ECC Key slot specific field names."""
        s0 = str(self.ecckey_slot_0_7)
        s1 = str(self.ecckey_slot_8_15)
        s2 = str(self.ecckey_slot_16_23)
        s3 = str(self.ecckey_slot_24_31)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )


class EddsaSignConfig(UapMultiSlotConfig):
    """UAP EdDSA Sign configuration (CFG_UAP_EDDSA_SIGN @ 0x144).

    Controls which pairing key slots can perform EdDSA signing.
    Has 4 permission fields for ECC Key slot groups 0-7, 8-15, 16-23, 24-31.
    """

    @property
    def ecckey_slot_0_7(self) -> UapPermissionField:
        """Permission field for ECC Key slots 0-7."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_0_7_POS)

    @ecckey_slot_0_7.setter
    def ecckey_slot_0_7(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_0_7_POS, field)

    @property
    def ecckey_slot_8_15(self) -> UapPermissionField:
        """Permission field for ECC Key slots 8-15."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_8_15_POS)

    @ecckey_slot_8_15.setter
    def ecckey_slot_8_15(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_8_15_POS, field)

    @property
    def ecckey_slot_16_23(self) -> UapPermissionField:
        """Permission field for ECC Key slots 16-23."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_16_23_POS)

    @ecckey_slot_16_23.setter
    def ecckey_slot_16_23(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_16_23_POS, field)

    @property
    def ecckey_slot_24_31(self) -> UapPermissionField:
        """Permission field for ECC Key slots 24-31."""
        return self._get_slot_field(UAP_ECCKEY_SLOT_24_31_POS)

    @ecckey_slot_24_31.setter
    def ecckey_slot_24_31(self, field: UapPermissionField) -> None:
        self._set_slot_field(UAP_ECCKEY_SLOT_24_31_POS, field)

    def to_dict(self) -> dict:
        """Export fields as dictionary."""
        return {
            'ecckey_slot_0_7': self.ecckey_slot_0_7.to_dict(),
            'ecckey_slot_8_15': self.ecckey_slot_8_15.to_dict(),
            'ecckey_slot_16_23': self.ecckey_slot_16_23.to_dict(),
            'ecckey_slot_24_31': self.ecckey_slot_24_31.to_dict()
        }

    def __str__(self) -> str:
        """Table row with ECC Key slot specific field names."""
        s0 = str(self.ecckey_slot_0_7)
        s1 = str(self.ecckey_slot_8_15)
        s2 = str(self.ecckey_slot_16_23)
        s3 = str(self.ecckey_slot_24_31)
        return "{:26s} | {} || {} || {} || {} |".format(
            self.__class__.__name__,
            s0, s1, s2, s3
        )
