"""Tests for UAP Operations configuration classes.

This module tests:
- PingConfig
- RandomValueGetConfig
- MacAndDestroyConfig

All classes inherit from UapDualFieldConfig.
"""

import pytest
from tropicsquare.config.uap_operations import (
    PingConfig,
    RandomValueGetConfig,
    MacAndDestroyConfig
)
from tropicsquare.config.uap_base import UapDualFieldConfig


class TestPingConfig:
    """Test PingConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = PingConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = PingConfig(0x00001122)
        assert config.cfg_permissions.value == 0x22
        assert config.func_permissions.value == 0x11

    def test_str_representation(self):
        """Test __str__()."""
        config = PingConfig()
        result = str(config)
        assert 'PingConfig' in result


class TestRandomValueGetConfig:
    """Test RandomValueGetConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = RandomValueGetConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = RandomValueGetConfig(0x00003344)
        assert config.cfg_permissions.value == 0x44
        assert config.func_permissions.value == 0x33

    def test_str_representation(self):
        """Test __str__()."""
        config = RandomValueGetConfig()
        result = str(config)
        assert 'RandomValueGetConfig' in result


class TestMacAndDestroyConfig:
    """Test MacAndDestroyConfig class."""

    def test_inherits_from_uap_dual_field_config(self):
        """Test inheritance."""
        config = MacAndDestroyConfig()
        assert isinstance(config, UapDualFieldConfig)

    def test_cfg_and_func_permissions(self):
        """Test permissions properties."""
        config = MacAndDestroyConfig(0x00005566)
        assert config.cfg_permissions.value == 0x66
        assert config.func_permissions.value == 0x55

    def test_str_representation(self):
        """Test __str__()."""
        config = MacAndDestroyConfig()
        result = str(config)
        assert 'MacAndDestroyConfig' in result
