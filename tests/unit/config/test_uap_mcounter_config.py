"""Tests for UAP MCounter configuration classes."""

import pytest
from tropicsquare.config.uap_mcounter import (
    MCounterInitConfig,
    MCounterGetConfig,
    MCounterUpdateConfig,
)
from tropicsquare.config.uap_base import UapMultiSlotConfig, UapPermissionField


MCOUNTER_CONFIG_CLASSES = (
    MCounterInitConfig,
    MCounterGetConfig,
    MCounterUpdateConfig,
)

MCOUNTER_SLOT_FIELDS = (
    "mcounter_0_3",
    "mcounter_4_7",
    "mcounter_8_11",
    "mcounter_12_15",
)


@pytest.mark.parametrize("config_cls", MCOUNTER_CONFIG_CLASSES)
def test_inherits_from_uap_multi_slot_config(config_cls):
    assert isinstance(config_cls(), UapMultiSlotConfig)


@pytest.mark.parametrize("config_cls", MCOUNTER_CONFIG_CLASSES)
def test_slot_field_properties(config_cls):
    config = config_cls(0x78563412)
    expected = (0x12, 0x34, 0x56, 0x78)

    for field_name, expected_value in zip(MCOUNTER_SLOT_FIELDS, expected):
        field = getattr(config, field_name)
        assert isinstance(field, UapPermissionField)
        assert field.value == expected_value


@pytest.mark.parametrize("config_cls", MCOUNTER_CONFIG_CLASSES)
def test_to_dict_contains_slot_fields(config_cls):
    result = config_cls(0x00000000).to_dict()
    assert set(result.keys()) == set(MCOUNTER_SLOT_FIELDS)
