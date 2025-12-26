"""Tests for UAP Memory configuration classes.

This module tests:
- RMemDataWriteConfig
- RMemDataReadConfig
- RMemDataEraseConfig

All classes inherit from UapDualFieldConfig.
"""

import pytest
from tropicsquare.config.uap_memory import (
    RMemDataWriteConfig,
    RMemDataReadConfig,
    RMemDataEraseConfig
)
from tropicsquare.config.uap_base import UapDualFieldConfig


class TestRMemDataWriteConfig:
    """Test RMemDataWriteConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = RMemDataWriteConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = RMemDataWriteConfig(0x00000F0A)
        assert config.cfg_permissions.value == 0x0A
        assert config.func_permissions.value == 0x0F

    def test_str_representation(self):
        """Test __str__()."""
        config = RMemDataWriteConfig()
        result = str(config)
        assert 'RMemDataWriteConfig' in result


class TestRMemDataReadConfig:
    """Test RMemDataReadConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = RMemDataReadConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = RMemDataReadConfig(0x00000505)
        assert config.cfg_permissions.value == 0x05
        assert config.func_permissions.value == 0x05

    def test_str_representation(self):
        """Test __str__()."""
        config = RMemDataReadConfig()
        result = str(config)
        assert 'RMemDataReadConfig' in result


class TestRMemDataEraseConfig:
    """Test RMemDataEraseConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = RMemDataEraseConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = RMemDataEraseConfig(0x0000ABCD)
        assert config.cfg_permissions.value == 0xCD
        assert config.func_permissions.value == 0xAB

    def test_str_representation(self):
        """Test __str__()."""
        config = RMemDataEraseConfig()
        result = str(config)
        assert 'RMemDataEraseConfig' in result
