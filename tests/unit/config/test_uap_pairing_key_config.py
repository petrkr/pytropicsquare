"""Tests for UAP Pairing Key configuration classes.

This module tests:
- PairingKeyWriteConfig
- PairingKeyReadConfig
- PairingKeyInvalidateConfig

All classes inherit from UapMultiSlotConfig.
"""

import pytest
from tropicsquare.config.uap_pairing_key import (
    PairingKeyWriteConfig,
    PairingKeyReadConfig,
    PairingKeyInvalidateConfig
)
from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField


class TestPairingKeyWriteConfig:
    """Test PairingKeyWriteConfig class."""

    def test_inherits_from_uap_multi_slot_config(self):
        """Test inheritance."""
        config = PairingKeyWriteConfig()
        assert isinstance(config, UapMultiSlotConfig)

    def test_get_slot_field(self):
        """Test getting slot field."""
        config = PairingKeyWriteConfig(0x0000AB00)
        field = config._get_slot_field(8)
        assert isinstance(field, UapPermissionField)
        assert field.value == 0xAB

    def test_set_slot_field(self):
        """Test setting slot field."""
        config = PairingKeyWriteConfig(0x00000000)
        config._set_slot_field(16, UapPermissionField(0xCD))
        assert config._value == 0x00CD0000

    def test_str_representation(self):
        """Test __str__()."""
        config = PairingKeyWriteConfig()
        result = str(config)
        assert 'PairingKeyWriteConfig' in result


class TestPairingKeyReadConfig:
    """Test PairingKeyReadConfig class."""

    def test_inherits_from_uap_multi_slot_config(self):
        """Test inheritance."""
        config = PairingKeyReadConfig()
        assert isinstance(config, UapMultiSlotConfig)

    def test_get_slot_field(self):
        """Test getting slot field."""
        config = PairingKeyReadConfig(0x00EF0000)
        field = config._get_slot_field(16)
        assert field.value == 0xEF

    def test_set_slot_field(self):
        """Test setting slot field."""
        config = PairingKeyReadConfig(0x00000000)
        config._set_slot_field(24, UapPermissionField(0x12))
        assert config._value == 0x12000000

    def test_str_representation(self):
        """Test __str__()."""
        config = PairingKeyReadConfig()
        result = str(config)
        assert 'PairingKeyReadConfig' in result


class TestPairingKeyInvalidateConfig:
    """Test PairingKeyInvalidateConfig class."""

    def test_inherits_from_uap_multi_slot_config(self):
        """Test inheritance."""
        config = PairingKeyInvalidateConfig()
        assert isinstance(config, UapMultiSlotConfig)

    def test_get_slot_field(self):
        """Test getting slot field."""
        config = PairingKeyInvalidateConfig(0x000000AB)
        field = config._get_slot_field(0)
        assert field.value == 0xAB

    def test_set_slot_field(self):
        """Test setting slot field."""
        config = PairingKeyInvalidateConfig(0x00000000)
        config._set_slot_field(8, UapPermissionField(0x34))
        assert config._value == 0x00003400

    def test_str_representation(self):
        """Test __str__()."""
        config = PairingKeyInvalidateConfig()
        result = str(config)
        assert 'PairingKeyInvalidateConfig' in result
