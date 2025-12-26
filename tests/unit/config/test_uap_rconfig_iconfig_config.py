"""Tests for UAP RConfig/IConfig configuration classes.

This module tests:
- RConfigWriteEraseConfig
- RConfigReadConfig
- IConfigWriteConfig
- IConfigReadConfig
"""

import pytest
from tropicsquare.config.uap_rconfig_iconfig import (
    RConfigWriteEraseConfig,
    RConfigReadConfig,
    IConfigWriteConfig,
    IConfigReadConfig
)
from tropicsquare.config.uap_base import UapSingleFieldConfig, UapDualFieldConfig


class TestRConfigWriteEraseConfig:
    """Test RConfigWriteEraseConfig class."""

    def test_inherits_from_uap_single_field_config(self):
        """Test inheritance."""
        config = RConfigWriteEraseConfig()
        assert isinstance(config, UapSingleFieldConfig)

    def test_permissions_property(self):
        """Test permissions property."""
        config = RConfigWriteEraseConfig(0x00000088)
        assert config.permissions.value == 0x88

    def test_str_representation(self):
        """Test __str__()."""
        config = RConfigWriteEraseConfig()
        result = str(config)
        assert 'RConfigWriteEraseConfig' in result


class TestRConfigReadConfig:
    """Test RConfigReadConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = RConfigReadConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = RConfigReadConfig(0x00007788)
        assert config.cfg_permissions.value == 0x88
        assert config.func_permissions.value == 0x77

    def test_str_representation(self):
        """Test __str__()."""
        config = RConfigReadConfig()
        result = str(config)
        assert 'RConfigReadConfig' in result


class TestIConfigWriteConfig:
    """Test IConfigWriteConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = IConfigWriteConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = IConfigWriteConfig(0x00009900)
        assert config.cfg_permissions.value == 0x00
        assert config.func_permissions.value == 0x99

    def test_str_representation(self):
        """Test __str__()."""
        config = IConfigWriteConfig()
        result = str(config)
        assert 'IConfigWriteConfig' in result


class TestIConfigReadConfig:
    """Test IConfigReadConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = IConfigReadConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = IConfigReadConfig(0x0000AABB)
        assert config.cfg_permissions.value == 0xBB
        assert config.func_permissions.value == 0xAA

    def test_str_representation(self):
        """Test __str__()."""
        config = IConfigReadConfig()
        result = str(config)
        assert 'IConfigReadConfig' in result
