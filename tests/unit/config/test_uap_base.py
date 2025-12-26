"""Tests for UAP Base classes.

This module tests:
- UapPermissionField class (8-bit permission field for 4 pairing key slots)
- UapSingleFieldConfig class (config with single 8-bit permission field)
- UapDualFieldConfig class (config with two 8-bit permission fields)
- UapMultiSlotConfig class (config with 4 slots, each with 8-bit permission field)
"""

import pytest
from tropicsquare.config.uap_base import (
    UapPermissionField,
    UapSingleFieldConfig,
    UapDualFieldConfig,
    UapMultiSlotConfig
)
from tropicsquare.config.base import BaseConfig


class TestUapPermissionFieldInitialization:
    """Test UapPermissionField initialization."""

    def test_default_initialization(self):
        """Test default initialization (all slots have access)."""
        field = UapPermissionField()
        assert field._value == 0xFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        field = UapPermissionField(0x0F)
        assert field._value == 0x0F

    def test_value_masked_to_8_bits(self):
        """Test that value is masked to 8 bits."""
        field = UapPermissionField(0x1FF)  # 9 bits
        assert field._value == 0xFF  # Only lower 8 bits


class TestUapPermissionFieldSlotPermissions:
    """Test UapPermissionField slot permission getters/setters."""

    def test_get_slot_permission_slot_0(self):
        """Test getting slot 0 permission."""
        field = UapPermissionField(0x01)  # Only slot 0
        assert field.get_slot_permission(0) is True
        assert field.get_slot_permission(1) is False

    def test_get_slot_permission_slot_3(self):
        """Test getting slot 3 permission."""
        field = UapPermissionField(0x08)  # Only slot 3 (bit 3)
        assert field.get_slot_permission(3) is True
        assert field.get_slot_permission(0) is False

    def test_get_slot_permission_invalid_slot_raises_error(self):
        """Test that invalid slot number raises ValueError."""
        field = UapPermissionField()
        with pytest.raises(ValueError) as exc_info:
            field.get_slot_permission(4)
        assert "Slot must be 0-3" in str(exc_info.value)

    def test_set_slot_permission_grant_access(self):
        """Test setting slot permission to grant access."""
        field = UapPermissionField(0x00)
        field.set_slot_permission(0, True)
        assert field._value == 0x01
        assert field.get_slot_permission(0) is True

    def test_set_slot_permission_deny_access(self):
        """Test setting slot permission to deny access."""
        field = UapPermissionField(0xFF)
        field.set_slot_permission(2, False)
        assert field._value == 0xFB  # 0xFF & ~0x04
        assert field.get_slot_permission(2) is False

    def test_set_slot_permission_invalid_slot_raises_error(self):
        """Test that setting invalid slot raises ValueError."""
        field = UapPermissionField()
        with pytest.raises(ValueError) as exc_info:
            field.set_slot_permission(5, True)
        assert "Slot must be 0-3" in str(exc_info.value)


class TestUapPermissionFieldProperties:
    """Test UapPermissionField slot properties."""

    def test_pkey_slot_0_getter(self):
        """Test pkey_slot_0 property getter."""
        field = UapPermissionField(0x01)
        assert field.pkey_slot_0 is True

    def test_pkey_slot_0_setter(self):
        """Test pkey_slot_0 property setter."""
        field = UapPermissionField(0x00)
        field.pkey_slot_0 = True
        assert field._value == 0x01

    def test_pkey_slot_1_getter(self):
        """Test pkey_slot_1 property getter."""
        field = UapPermissionField(0x02)
        assert field.pkey_slot_1 is True

    def test_pkey_slot_1_setter(self):
        """Test pkey_slot_1 property setter."""
        field = UapPermissionField(0x00)
        field.pkey_slot_1 = True
        assert field._value == 0x02

    def test_pkey_slot_2_getter(self):
        """Test pkey_slot_2 property getter."""
        field = UapPermissionField(0x04)
        assert field.pkey_slot_2 is True

    def test_pkey_slot_2_setter(self):
        """Test pkey_slot_2 property setter."""
        field = UapPermissionField(0x00)
        field.pkey_slot_2 = True
        assert field._value == 0x04

    def test_pkey_slot_3_getter(self):
        """Test pkey_slot_3 property getter."""
        field = UapPermissionField(0x08)
        assert field.pkey_slot_3 is True

    def test_pkey_slot_3_setter(self):
        """Test pkey_slot_3 property setter."""
        field = UapPermissionField(0x00)
        field.pkey_slot_3 = True
        assert field._value == 0x08

    def test_value_property_getter(self):
        """Test value property getter."""
        field = UapPermissionField(0xAB)
        assert field.value == 0xAB

    def test_value_property_setter(self):
        """Test value property setter."""
        field = UapPermissionField(0x00)
        field.value = 0xCD
        assert field._value == 0xCD

    def test_value_property_setter_masks_to_8_bits(self):
        """Test that value setter masks to 8 bits."""
        field = UapPermissionField(0x00)
        field.value = 0x1FF
        assert field._value == 0xFF


class TestUapPermissionFieldToDict:
    """Test UapPermissionField to_dict() method."""

    def test_to_dict_all_slots_enabled(self):
        """Test to_dict with all slots enabled."""
        field = UapPermissionField(0x0F)
        result = field.to_dict()
        assert result == {
            'pkey_slot_0': True,
            'pkey_slot_1': True,
            'pkey_slot_2': True,
            'pkey_slot_3': True
        }

    def test_to_dict_no_slots_enabled(self):
        """Test to_dict with no slots enabled."""
        field = UapPermissionField(0x00)
        result = field.to_dict()
        assert result == {
            'pkey_slot_0': False,
            'pkey_slot_1': False,
            'pkey_slot_2': False,
            'pkey_slot_3': False
        }

    def test_to_dict_mixed_slots(self):
        """Test to_dict with mixed slot permissions."""
        field = UapPermissionField(0x05)  # Slots 0 and 2
        result = field.to_dict()
        assert result == {
            'pkey_slot_0': True,
            'pkey_slot_1': False,
            'pkey_slot_2': True,
            'pkey_slot_3': False
        }


class TestUapSingleFieldConfigInitialization:
    """Test UapSingleFieldConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization (all access)."""
        config = UapSingleFieldConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = UapSingleFieldConfig(0x12345678)
        assert config._value == 0x12345678


class TestUapSingleFieldConfigPermissions:
    """Test UapSingleFieldConfig permissions property."""

    def test_permissions_getter(self):
        """Test permissions property returns UapPermissionField."""
        config = UapSingleFieldConfig(0x0000000F)
        perms = config.permissions
        assert isinstance(perms, UapPermissionField)
        assert perms.value == 0x0F

    def test_permissions_setter_with_field(self):
        """Test permissions setter with UapPermissionField."""
        config = UapSingleFieldConfig(0x00000000)
        field = UapPermissionField(0xAB)
        config.permissions = field
        assert config._value & 0xFF == 0xAB

    def test_permissions_setter_with_int(self):
        """Test permissions setter with integer value wrapped in UapPermissionField."""
        config = UapSingleFieldConfig(0x00000000)
        config.permissions = UapPermissionField(0xCD)
        assert config._value & 0xFF == 0xCD

    def test_permissions_setter_preserves_other_bits(self):
        """Test that permissions setter preserves other bits."""
        config = UapSingleFieldConfig(0xFFFFFF00)
        config.permissions = UapPermissionField(0x12)
        assert config._value == 0xFFFFFF12


class TestUapSingleFieldConfigToDict:
    """Test UapSingleFieldConfig to_dict() method."""

    def test_to_dict(self):
        """Test to_dict returns permissions dict."""
        config = UapSingleFieldConfig(0x0000000F)
        result = config.to_dict()
        assert 'permissions' in result
        assert result['permissions'] == {
            'pkey_slot_0': True,
            'pkey_slot_1': True,
            'pkey_slot_2': True,
            'pkey_slot_3': True
        }


class TestUapSingleFieldConfigInheritance:
    """Test UapSingleFieldConfig inheritance."""

    def test_inherits_from_base_config(self):
        """Test that UapSingleFieldConfig inherits from BaseConfig."""
        config = UapSingleFieldConfig()
        assert isinstance(config, BaseConfig)


class TestUapDualFieldConfigInitialization:
    """Test UapDualFieldConfig initialization."""

    def test_default_initialization(self):
        """Test default initialization (all access)."""
        config = UapDualFieldConfig()
        assert config._value == 0xFFFFFFFF

    def test_custom_value_initialization(self):
        """Test initialization with custom value."""
        config = UapDualFieldConfig(0x12345678)
        assert config._value == 0x12345678


class TestUapDualFieldConfigCfgPermissions:
    """Test UapDualFieldConfig cfg_permissions property."""

    def test_cfg_permissions_getter(self):
        """Test cfg_permissions property returns UapPermissionField."""
        config = UapDualFieldConfig(0x000000AB)
        perms = config.cfg_permissions
        assert isinstance(perms, UapPermissionField)
        assert perms.value == 0xAB

    def test_cfg_permissions_setter_with_field(self):
        """Test cfg_permissions setter with UapPermissionField."""
        config = UapDualFieldConfig(0x00000000)
        field = UapPermissionField(0x12)
        config.cfg_permissions = field
        assert config._value & 0xFF == 0x12

    def test_cfg_permissions_setter_with_int(self):
        """Test cfg_permissions setter with integer value wrapped in UapPermissionField."""
        config = UapDualFieldConfig(0x00000000)
        config.cfg_permissions = UapPermissionField(0x34)
        assert config._value & 0xFF == 0x34

    def test_cfg_permissions_setter_preserves_other_bits(self):
        """Test that cfg_permissions setter preserves other bits."""
        config = UapDualFieldConfig(0xFFFFFF00)
        config.cfg_permissions = UapPermissionField(0x56)
        assert config._value == 0xFFFFFF56


class TestUapDualFieldConfigFuncPermissions:
    """Test UapDualFieldConfig func_permissions property."""

    def test_func_permissions_getter(self):
        """Test func_permissions property returns UapPermissionField."""
        config = UapDualFieldConfig(0x0000AB00)
        perms = config.func_permissions
        assert isinstance(perms, UapPermissionField)
        assert perms.value == 0xAB

    def test_func_permissions_setter_with_field(self):
        """Test func_permissions setter with UapPermissionField."""
        config = UapDualFieldConfig(0x00000000)
        field = UapPermissionField(0x12)
        config.func_permissions = field
        assert (config._value >> 8) & 0xFF == 0x12

    def test_func_permissions_setter_with_int(self):
        """Test func_permissions setter with integer value wrapped in UapPermissionField."""
        config = UapDualFieldConfig(0x00000000)
        config.func_permissions = UapPermissionField(0x34)
        assert (config._value >> 8) & 0xFF == 0x34

    def test_func_permissions_setter_preserves_other_bits(self):
        """Test that func_permissions setter preserves other bits."""
        config = UapDualFieldConfig(0xFFFF00FF)
        config.func_permissions = UapPermissionField(0x56)
        assert config._value == 0xFFFF56FF


class TestUapDualFieldConfigToDict:
    """Test UapDualFieldConfig to_dict() method."""

    def test_to_dict(self):
        """Test to_dict returns both cfg and func permissions."""
        config = UapDualFieldConfig(0x00000F0A)
        result = config.to_dict()

        assert 'cfg_permissions' in result
        assert result['cfg_permissions'] == {
            'pkey_slot_0': False,
            'pkey_slot_1': True,
            'pkey_slot_2': False,
            'pkey_slot_3': True
        }

        assert 'func_permissions' in result
        assert result['func_permissions'] == {
            'pkey_slot_0': True,
            'pkey_slot_1': True,
            'pkey_slot_2': True,
            'pkey_slot_3': True
        }


class TestUapDualFieldConfigInheritance:
    """Test UapDualFieldConfig inheritance."""

    def test_inherits_from_base_config(self):
        """Test that UapDualFieldConfig inherits from BaseConfig."""
        config = UapDualFieldConfig()
        assert isinstance(config, BaseConfig)


class TestUapMultiSlotConfigGetSetSlotField:
    """Test UapMultiSlotConfig _get_slot_field and _set_slot_field methods."""

    def test_get_slot_field_at_position_0(self):
        """Test getting slot field at position 0."""
        config = UapMultiSlotConfig(0x000000AB)
        field = config._get_slot_field(0)
        assert isinstance(field, UapPermissionField)
        assert field.value == 0xAB

    def test_get_slot_field_at_position_8(self):
        """Test getting slot field at position 8."""
        config = UapMultiSlotConfig(0x0000CD00)
        field = config._get_slot_field(8)
        assert isinstance(field, UapPermissionField)
        assert field.value == 0xCD

    def test_get_slot_field_at_position_16(self):
        """Test getting slot field at position 16."""
        config = UapMultiSlotConfig(0x00EF0000)
        field = config._get_slot_field(16)
        assert isinstance(field, UapPermissionField)
        assert field.value == 0xEF

    def test_get_slot_field_at_position_24(self):
        """Test getting slot field at position 24."""
        config = UapMultiSlotConfig(0x12000000)
        field = config._get_slot_field(24)
        assert isinstance(field, UapPermissionField)
        assert field.value == 0x12

    def test_set_slot_field_with_field_object(self):
        """Test setting slot field with UapPermissionField object."""
        config = UapMultiSlotConfig(0x00000000)
        field = UapPermissionField(0xAB)
        config._set_slot_field(8, field)
        assert config._value == 0x0000AB00

    def test_set_slot_field_with_int(self):
        """Test setting slot field with integer value wrapped in UapPermissionField."""
        config = UapMultiSlotConfig(0x00000000)
        config._set_slot_field(16, UapPermissionField(0xCD))
        assert config._value == 0x00CD0000

    def test_set_slot_field_preserves_other_fields(self):
        """Test that setting slot field preserves other fields."""
        config = UapMultiSlotConfig(0xAABBCCDD)
        config._set_slot_field(8, UapPermissionField(0x12))
        assert config._value == 0xAABB12DD


class TestUapMultiSlotConfigInheritance:
    """Test UapMultiSlotConfig inheritance."""

    def test_inherits_from_base_config(self):
        """Test that UapMultiSlotConfig inherits from BaseConfig."""
        config = UapMultiSlotConfig()
        assert isinstance(config, BaseConfig)
