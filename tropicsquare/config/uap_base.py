"""Base classes and helpers for User Access Policy (UAP) configuration"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.constants import (
    UAP_PKEY_SLOT_0_BIT,
    UAP_PKEY_SLOT_1_BIT,
    UAP_PKEY_SLOT_2_BIT,
    UAP_PKEY_SLOT_3_BIT
)


class UapPermissionField:
    """Represents an 8-bit UAP permission field.

        Each field contains permission bits for 4 pairing key slots:

        - Bit 0: Pairing Key slot 0 has access
        - Bit 1: Pairing Key slot 1 has access
        - Bit 2: Pairing Key slot 2 has access
        - Bit 3: Pairing Key slot 3 has access
        - Bits 4-7: Reserved
    """

    def __init__(self, value: int = 0xFF) -> None:
        """Initialize permission field.

            :param value: 8-bit permission value (default: 0xFF = all slots have access)
        """
        self._value = value & 0xFF

    def get_slot_permission(self, slot: int) -> bool:
        """Check if pairing key slot has access.

            :param slot: Slot number (0-3)

            :returns: True if slot has access
            :rtype: bool
        """
        if not 0 <= slot <= 3:
            raise ValueError("Slot must be 0-3, got {}".format(slot))
        return bool((self._value >> slot) & 1)

    def set_slot_permission(self, slot: int, has_access: bool) -> None:
        """Set permission for pairing key slot.

            :param slot: Slot number (0-3)
            :param has_access: True to grant access, False to deny
        """
        if not 0 <= slot <= 3:
            raise ValueError("Slot must be 0-3, got {}".format(slot))
        if has_access:
            self._value |= (1 << slot)
        else:
            self._value &= ~(1 << slot)

    @property
    def pkey_slot_0(self) -> bool:
        """Pairing Key slot 0 has access."""
        return self.get_slot_permission(0)

    @pkey_slot_0.setter
    def pkey_slot_0(self, value: bool) -> None:
        self.set_slot_permission(0, value)

    @property
    def pkey_slot_1(self) -> bool:
        """Pairing Key slot 1 has access."""
        return self.get_slot_permission(1)

    @pkey_slot_1.setter
    def pkey_slot_1(self, value: bool) -> None:
        self.set_slot_permission(1, value)

    @property
    def pkey_slot_2(self) -> bool:
        """Pairing Key slot 2 has access."""
        return self.get_slot_permission(2)

    @pkey_slot_2.setter
    def pkey_slot_2(self, value: bool) -> None:
        self.set_slot_permission(2, value)

    @property
    def pkey_slot_3(self) -> bool:
        """Pairing Key slot 3 has access."""
        return self.get_slot_permission(3)

    @pkey_slot_3.setter
    def pkey_slot_3(self, value: bool) -> None:
        self.set_slot_permission(3, value)

    @property
    def value(self) -> int:
        """Raw 8-bit value."""
        return self._value

    @value.setter
    def value(self, val: int) -> None:
        self._value = val & 0xFF

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            'pkey_slot_0': self.pkey_slot_0,
            'pkey_slot_1': self.pkey_slot_1,
            'pkey_slot_2': self.pkey_slot_2,
            'pkey_slot_3': self.pkey_slot_3
        }

    def __str__(self) -> str:
        slots = []
        for i in range(4):
            if self.get_slot_permission(i):
                slots.append(str(i))
        if slots:
            return "slots[{}]".format(",".join(slots))
        else:
            return "no_access"


class UapMultiSlotConfig(BaseConfig):
    """Base class for UAP configs with multiple slots.

    Used for configs that have 4 slots, each with 8-bit permission field.
    """

    def _get_slot_field(self, slot_pos):
        """Get 8-bit permission field at slot position.

            :param slot_pos: Bit position of slot (0, 8, 16, or 24)

            :returns: Permission field at the specified slot position
            :rtype: UapPermissionField
        """
        field_value = (self._value >> slot_pos) & 0xFF
        return UapPermissionField(field_value)

    def _set_slot_field(self, slot_pos, field):
        """Set 8-bit permission field at slot position.

            :param slot_pos: Bit position of slot (0, 8, 16, or 24)
            :param field: UapPermissionField or int (8-bit value)
        """
        if isinstance(field, UapPermissionField):
            field_value = field.value
        else:
            field_value = field & 0xFF

        # Clear existing field and set new value
        mask = 0xFF << slot_pos
        self._value = (self._value & ~mask) | (field_value << slot_pos)


class UapSingleFieldConfig(BaseConfig):
    """Base class for UAP configs with single 8-bit permission field."""

    def __init__(self, value: int = 0xFFFFFFFF) -> None:
        """Initialize with default all-access value."""
        super().__init__(value)

    @property
    def permissions(self) -> UapPermissionField:
        """Get permission field (8 bits at position 0)."""
        field_value = self._value & 0xFF
        return UapPermissionField(field_value)

    @permissions.setter
    def permissions(self, field) -> None:
        """Set permission field."""
        if isinstance(field, UapPermissionField):
            field_value = field.value
        else:
            field_value = field & 0xFF
        self._value = (self._value & ~0xFF) | field_value

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            'permissions': self.permissions.to_dict()
        }


class UapDualFieldConfig(BaseConfig):
    """Base class for UAP configs with two 8-bit permission fields (CFG and FUNC)."""

    def __init__(self, value: int = 0xFFFFFFFF) -> None:
        """Initialize with default all-access value."""
        super().__init__(value)

    @property
    def cfg_permissions(self) -> UapPermissionField:
        """Get CFG permission field (8 bits at position 0)."""
        field_value = self._value & 0xFF
        return UapPermissionField(field_value)

    @cfg_permissions.setter
    def cfg_permissions(self, field) -> None:
        """Set CFG permission field."""
        if isinstance(field, UapPermissionField):
            field_value = field.value
        else:
            field_value = field & 0xFF
        self._value = (self._value & ~0xFF) | field_value

    @property
    def func_permissions(self) -> UapPermissionField:
        """Get FUNC permission field (8 bits at position 8)."""
        field_value = (self._value >> 8) & 0xFF
        return UapPermissionField(field_value)

    @func_permissions.setter
    def func_permissions(self, field) -> None:
        """Set FUNC permission field."""
        if isinstance(field, UapPermissionField):
            field_value = field.value
        else:
            field_value = field & 0xFF
        self._value = (self._value & ~0xFF00) | (field_value << 8)

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            'cfg_permissions': self.cfg_permissions.to_dict(),
            'func_permissions': self.func_permissions.to_dict()
        }
