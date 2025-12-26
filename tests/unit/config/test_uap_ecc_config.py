"""Tests for UAP ECC configuration classes.

This module tests:
- EccKeyGenerateConfig
- EccKeyStoreConfig
- EccKeyReadConfig
- EccKeyEraseConfig
- EcdsaSignConfig
- EddsaSignConfig

All classes inherit from UapDualFieldConfig and are tested for:
- cfg_permissions and func_permissions properties
- to_dict() method
- String representation
- Inheritance from UapDualFieldConfig
"""

import pytest
from tropicsquare.config.uap_ecc import (
    EccKeyGenerateConfig,
    EccKeyStoreConfig,
    EccKeyReadConfig,
    EccKeyEraseConfig,
    EcdsaSignConfig,
    EddsaSignConfig
)
from tropicsquare.config.uap_base import UapDualFieldConfig, UapPermissionField


class TestEccKeyGenerateConfig:
    """Test EccKeyGenerateConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test that EccKeyGenerateConfig inherits from UapDualFieldConfig."""
        config = EccKeyGenerateConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_permissions_property(self):
        """Test cfg_permissions property."""
        config = EccKeyGenerateConfig(0x000000AB)
        perms = config.cfg_permissions
        assert isinstance(perms, UapPermissionField)
        assert perms.value == 0xAB

    def test_func_permissions_property(self):
        """Test func_permissions property."""
        config = EccKeyGenerateConfig(0x0000CD00)
        perms = config.func_permissions
        assert isinstance(perms, UapPermissionField)
        assert perms.value == 0xCD

    def test_str_representation(self):
        """Test __str__() method."""
        config = EccKeyGenerateConfig(0x00000F0A)
        result = str(config)
        assert 'EccKeyGenerateConfig' in result
        assert 'cfg=' in result
        assert 'func=' in result


class TestEccKeyStoreConfig:
    """Test EccKeyStoreConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test that EccKeyStoreConfig inherits from UapDualFieldConfig."""
        config = EccKeyStoreConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_permissions_property(self):
        """Test cfg_permissions property."""
        config = EccKeyStoreConfig(0x00000012)
        perms = config.cfg_permissions
        assert perms.value == 0x12

    def test_func_permissions_property(self):
        """Test func_permissions property."""
        config = EccKeyStoreConfig(0x00003400)
        perms = config.func_permissions
        assert perms.value == 0x34

    def test_str_representation(self):
        """Test __str__() method."""
        config = EccKeyStoreConfig(0x00000505)
        result = str(config)
        assert 'EccKeyStoreConfig' in result


class TestEccKeyReadConfig:
    """Test EccKeyReadConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test that EccKeyReadConfig inherits from UapDualFieldConfig."""
        config = EccKeyReadConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_permissions_property(self):
        """Test cfg_permissions property."""
        config = EccKeyReadConfig(0x00000056)
        perms = config.cfg_permissions
        assert perms.value == 0x56

    def test_func_permissions_property(self):
        """Test func_permissions property."""
        config = EccKeyReadConfig(0x00007800)
        perms = config.func_permissions
        assert perms.value == 0x78

    def test_str_representation(self):
        """Test __str__() method."""
        config = EccKeyReadConfig(0x00000A0B)
        result = str(config)
        assert 'EccKeyReadConfig' in result


class TestEccKeyEraseConfig:
    """Test EccKeyEraseConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test that EccKeyEraseConfig inherits from UapDualFieldConfig."""
        config = EccKeyEraseConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_permissions_property(self):
        """Test cfg_permissions property."""
        config = EccKeyEraseConfig(0x0000009A)
        perms = config.cfg_permissions
        assert perms.value == 0x9A

    def test_func_permissions_property(self):
        """Test func_permissions property."""
        config = EccKeyEraseConfig(0x0000BC00)
        perms = config.func_permissions
        assert perms.value == 0xBC

    def test_str_representation(self):
        """Test __str__() method."""
        config = EccKeyEraseConfig(0x00000C0D)
        result = str(config)
        assert 'EccKeyEraseConfig' in result


class TestEcdsaSignConfig:
    """Test EcdsaSignConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test that EcdsaSignConfig inherits from UapDualFieldConfig."""
        config = EcdsaSignConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_permissions_property(self):
        """Test cfg_permissions property."""
        config = EcdsaSignConfig(0x000000DE)
        perms = config.cfg_permissions
        assert perms.value == 0xDE

    def test_func_permissions_property(self):
        """Test func_permissions property."""
        config = EcdsaSignConfig(0x0000EF00)
        perms = config.func_permissions
        assert perms.value == 0xEF

    def test_str_representation(self):
        """Test __str__() method."""
        config = EcdsaSignConfig(0x00000E0F)
        result = str(config)
        assert 'EcdsaSignConfig' in result


class TestEddsaSignConfig:
    """Test EddsaSignConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test that EddsaSignConfig inherits from UapDualFieldConfig."""
        config = EddsaSignConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_permissions_property(self):
        """Test cfg_permissions property."""
        config = EddsaSignConfig(0x00000012)
        perms = config.cfg_permissions
        assert perms.value == 0x12

    def test_func_permissions_property(self):
        """Test func_permissions property."""
        config = EddsaSignConfig(0x00003400)
        perms = config.func_permissions
        assert perms.value == 0x34

    def test_str_representation(self):
        """Test __str__() method."""
        config = EddsaSignConfig(0x00001011)
        result = str(config)
        assert 'EddsaSignConfig' in result


class TestAllEccConfigsToDict:
    """Test to_dict() method for all ECC config classes."""

    def test_ecc_key_generate_to_dict(self):
        """Test EccKeyGenerateConfig to_dict()."""
        config = EccKeyGenerateConfig(0x00000F0A)
        result = config.to_dict()
        assert 'cfg_permissions' in result
        assert 'func_permissions' in result

    def test_ecc_key_store_to_dict(self):
        """Test EccKeyStoreConfig to_dict()."""
        config = EccKeyStoreConfig(0x00000505)
        result = config.to_dict()
        assert 'cfg_permissions' in result
        assert 'func_permissions' in result

    def test_ecc_key_read_to_dict(self):
        """Test EccKeyReadConfig to_dict()."""
        config = EccKeyReadConfig(0x00000A0B)
        result = config.to_dict()
        assert 'cfg_permissions' in result
        assert 'func_permissions' in result

    def test_ecc_key_erase_to_dict(self):
        """Test EccKeyEraseConfig to_dict()."""
        config = EccKeyEraseConfig(0x00000C0D)
        result = config.to_dict()
        assert 'cfg_permissions' in result
        assert 'func_permissions' in result

    def test_ecdsa_sign_to_dict(self):
        """Test EcdsaSignConfig to_dict()."""
        config = EcdsaSignConfig(0x00000E0F)
        result = config.to_dict()
        assert 'cfg_permissions' in result
        assert 'func_permissions' in result

    def test_eddsa_sign_to_dict(self):
        """Test EddsaSignConfig to_dict()."""
        config = EddsaSignConfig(0x00001011)
        result = config.to_dict()
        assert 'cfg_permissions' in result
        assert 'func_permissions' in result
