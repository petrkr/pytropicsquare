"""Tests for UAP ECC configuration classes."""

import pytest
from tropicsquare.config.uap_ecc import (
    EccKeyGenerateConfig,
    EccKeyStoreConfig,
    EccKeyReadConfig,
    EccKeyEraseConfig,
    EcdsaSignConfig,
    EddsaSignConfig,
)
from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField


ECC_CONFIG_CLASSES = (
    EccKeyGenerateConfig,
    EccKeyStoreConfig,
    EccKeyReadConfig,
    EccKeyEraseConfig,
    EcdsaSignConfig,
    EddsaSignConfig,
)

ECC_SLOT_FIELDS = (
    "ecckey_slot_0_7",
    "ecckey_slot_8_15",
    "ecckey_slot_16_23",
    "ecckey_slot_24_31",
)


@pytest.mark.parametrize("config_cls", ECC_CONFIG_CLASSES)
def test_inherits_from_uap_multi_slot_config(config_cls):
    """All ECC configs are 4x8-bit multi-slot UAP configs."""
    assert isinstance(config_cls(), UapMultiSlotConfig)


@pytest.mark.parametrize("config_cls", ECC_CONFIG_CLASSES)
def test_slot_field_properties(config_cls):
    """Slot properties return expected byte-sized fields."""
    config = config_cls(0x44332211)
    expected = (0x11, 0x22, 0x33, 0x44)

    for field_name, expected_value in zip(ECC_SLOT_FIELDS, expected):
        field = getattr(config, field_name)
        assert isinstance(field, UapPermissionField)
        assert field.value == expected_value


@pytest.mark.parametrize("config_cls", ECC_CONFIG_CLASSES)
def test_to_dict_contains_slot_fields(config_cls):
    """to_dict uses ECC slot-based keys."""
    result = config_cls(0x00000000).to_dict()
    assert set(result.keys()) == set(ECC_SLOT_FIELDS)
