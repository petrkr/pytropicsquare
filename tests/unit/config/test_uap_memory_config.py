"""Tests for UAP Memory configuration classes."""

import pytest
from tropicsquare.config.uap_memory import (
    RMemDataWriteConfig,
    RMemDataReadConfig,
    RMemDataEraseConfig,
)
from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField


MEMORY_CONFIG_CLASSES = (
    RMemDataWriteConfig,
    RMemDataReadConfig,
    RMemDataEraseConfig,
)

MEMORY_SLOT_FIELDS = (
    "udata_slot_0_127",
    "udata_slot_128_255",
    "udata_slot_256_383",
    "udata_slot_384_511",
)


@pytest.mark.parametrize("config_cls", MEMORY_CONFIG_CLASSES)
def test_inherits_from_uap_multi_slot_config(config_cls):
    assert isinstance(config_cls(), UapMultiSlotConfig)


@pytest.mark.parametrize("config_cls", MEMORY_CONFIG_CLASSES)
def test_slot_field_properties(config_cls):
    config = config_cls(0x78563412)
    expected = (0x12, 0x34, 0x56, 0x78)

    for field_name, expected_value in zip(MEMORY_SLOT_FIELDS, expected):
        field = getattr(config, field_name)
        assert isinstance(field, UapPermissionField)
        assert field.value == expected_value


@pytest.mark.parametrize("config_cls", MEMORY_CONFIG_CLASSES)
def test_to_dict_contains_slot_fields(config_cls):
    result = config_cls(0x00000000).to_dict()
    assert set(result.keys()) == set(MEMORY_SLOT_FIELDS)
