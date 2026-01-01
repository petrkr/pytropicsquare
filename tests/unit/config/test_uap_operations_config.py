"""Tests for UAP Operations configuration classes."""

from tropicsquare.config.uap_operations import (
    PingConfig,
    RandomValueGetConfig,
    MacAndDestroyConfig,
)
from tropicsquare.config.uap_base import (
    UapSingleFieldConfig,
    UapMultiSlotConfig,
    UapPermissionField,
)


def test_ping_is_single_field_config():
    config = PingConfig(0x00001122)
    assert isinstance(config, UapSingleFieldConfig)
    assert config.permissions.value == 0x22


def test_random_value_get_is_single_field_config():
    config = RandomValueGetConfig(0x00003344)
    assert isinstance(config, UapSingleFieldConfig)
    assert config.permissions.value == 0x44


def test_mac_and_destroy_is_multi_slot_config():
    config = MacAndDestroyConfig(0x78563412)
    assert isinstance(config, UapMultiSlotConfig)

    assert isinstance(config.macandd0_31, UapPermissionField)
    assert isinstance(config.macandd32_63, UapPermissionField)
    assert isinstance(config.macandd64_95, UapPermissionField)
    assert isinstance(config.macandd96_127, UapPermissionField)

    assert config.macandd0_31.value == 0x12
    assert config.macandd32_63.value == 0x34
    assert config.macandd64_95.value == 0x56
    assert config.macandd96_127.value == 0x78


def test_mac_and_destroy_to_dict_slot_keys():
    result = MacAndDestroyConfig(0x00000000).to_dict()
    assert set(result.keys()) == {
        "macandd0_31",
        "macandd32_63",
        "macandd64_95",
        "macandd96_127",
    }
