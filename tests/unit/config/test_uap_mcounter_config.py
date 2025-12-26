"""Tests for UAP MCounter configuration classes.

This module tests:
- MCounterInitConfig
- MCounterGetConfig
- MCounterUpdateConfig

All classes inherit from UapDualFieldConfig.
"""

import pytest
from tropicsquare.config.uap_mcounter import (
    MCounterInitConfig,
    MCounterGetConfig,
    MCounterUpdateConfig
)
from tropicsquare.config.uap_base import UapDualFieldConfig


class TestMCounterInitConfig:
    """Test MCounterInitConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = MCounterInitConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = MCounterInitConfig(0x00001234)
        assert config.cfg_permissions.value == 0x34
        assert config.func_permissions.value == 0x12

    def test_str_representation(self):
        """Test __str__()."""
        config = MCounterInitConfig()
        result = str(config)
        assert 'MCounterInitConfig' in result


class TestMCounterGetConfig:
    """Test MCounterGetConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = MCounterGetConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = MCounterGetConfig(0x00005678)
        assert config.cfg_permissions.value == 0x78
        assert config.func_permissions.value == 0x56

    def test_str_representation(self):
        """Test __str__()."""
        config = MCounterGetConfig()
        result = str(config)
        assert 'MCounterGetConfig' in result


class TestMCounterUpdateConfig:
    """Test MCounterUpdateConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = MCounterUpdateConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = MCounterUpdateConfig(0x0000ABCD)
        assert config.cfg_permissions.value == 0xCD
        assert config.func_permissions.value == 0xAB

    def test_str_representation(self):
        """Test __str__()."""
        config = MCounterUpdateConfig()
        result = str(config)
        assert 'MCounterUpdateConfig' in result
