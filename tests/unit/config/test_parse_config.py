"""Tests for config parsing utility functions."""

import pytest
from tropicsquare.config import parse_config
from tropicsquare.config.startup import StartUpConfig
from tropicsquare.config.sensors import SensorsConfig
from tropicsquare.config.debug import DebugConfig
from tropicsquare.config.gpo import GpoConfig
from tropicsquare.config.sleep_mode import SleepModeConfig
from tropicsquare.config.uap_pairing_key import (
    PairingKeyWriteConfig,
    PairingKeyReadConfig,
    PairingKeyInvalidateConfig
)
from tropicsquare.config.uap_rconfig_iconfig import (
    RConfigWriteEraseConfig,
    RConfigReadConfig,
    IConfigWriteConfig,
    IConfigReadConfig
)
from tropicsquare.config.uap_operations import (
    PingConfig,
    RandomValueGetConfig,
    MacAndDestroyConfig
)
from tropicsquare.config.uap_memory import (
    RMemDataWriteConfig,
    RMemDataReadConfig,
    RMemDataEraseConfig
)
from tropicsquare.config.uap_ecc import (
    EccKeyGenerateConfig,
    EccKeyStoreConfig,
    EccKeyReadConfig,
    EccKeyEraseConfig,
    EcdsaSignConfig,
    EddsaSignConfig
)
from tropicsquare.config.uap_mcounter import (
    MCounterInitConfig,
    MCounterGetConfig,
    MCounterUpdateConfig
)
from tropicsquare.constants.config import (
    CFG_START_UP,
    CFG_SENSORS,
    CFG_DEBUG,
    CFG_GPO,
    CFG_SLEEP_MODE,
    CFG_UAP_PAIRING_KEY_WRITE,
    CFG_UAP_PAIRING_KEY_READ,
    CFG_UAP_PAIRING_KEY_INVALIDATE,
    CFG_UAP_R_CONFIG_WRITE_ERASE,
    CFG_UAP_R_CONFIG_READ,
    CFG_UAP_I_CONFIG_WRITE,
    CFG_UAP_I_CONFIG_READ,
    CFG_UAP_PING,
    CFG_UAP_R_MEM_DATA_WRITE,
    CFG_UAP_R_MEM_DATA_READ,
    CFG_UAP_R_MEM_DATA_ERASE,
    CFG_UAP_RANDOM_VALUE_GET,
    CFG_UAP_ECC_KEY_GENERATE,
    CFG_UAP_ECC_KEY_STORE,
    CFG_UAP_ECC_KEY_READ,
    CFG_UAP_ECC_KEY_ERASE,
    CFG_UAP_ECDSA_SIGN,
    CFG_UAP_EDDSA_SIGN,
    CFG_UAP_MCOUNTER_INIT,
    CFG_UAP_MCOUNTER_GET,
    CFG_UAP_MCOUNTER_UPDATE,
    CFG_UAP_MAC_AND_DESTROY
)


class TestParseConfig:
    """Test parse_config factory function."""

    def test_parse_startup_config(self):
        """Test parsing StartUpConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_START_UP, data)
        assert isinstance(result, StartUpConfig)

    def test_parse_sensors_config(self):
        """Test parsing SensorsConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_SENSORS, data)
        assert isinstance(result, SensorsConfig)

    def test_parse_debug_config(self):
        """Test parsing DebugConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_DEBUG, data)
        assert isinstance(result, DebugConfig)

    def test_parse_gpo_config(self):
        """Test parsing GpoConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_GPO, data)
        assert isinstance(result, GpoConfig)

    def test_parse_sleep_mode_config(self):
        """Test parsing SleepModeConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_SLEEP_MODE, data)
        assert isinstance(result, SleepModeConfig)

    def test_parse_pairing_key_write_config(self):
        """Test parsing PairingKeyWriteConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_PAIRING_KEY_WRITE, data)
        assert isinstance(result, PairingKeyWriteConfig)

    def test_parse_pairing_key_read_config(self):
        """Test parsing PairingKeyReadConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_PAIRING_KEY_READ, data)
        assert isinstance(result, PairingKeyReadConfig)

    def test_parse_pairing_key_invalidate_config(self):
        """Test parsing PairingKeyInvalidateConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_PAIRING_KEY_INVALIDATE, data)
        assert isinstance(result, PairingKeyInvalidateConfig)

    def test_parse_rconfig_write_erase_config(self):
        """Test parsing RConfigWriteEraseConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_R_CONFIG_WRITE_ERASE, data)
        assert isinstance(result, RConfigWriteEraseConfig)

    def test_parse_rconfig_read_config(self):
        """Test parsing RConfigReadConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_R_CONFIG_READ, data)
        assert isinstance(result, RConfigReadConfig)

    def test_parse_iconfig_write_config(self):
        """Test parsing IConfigWriteConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_I_CONFIG_WRITE, data)
        assert isinstance(result, IConfigWriteConfig)

    def test_parse_iconfig_read_config(self):
        """Test parsing IConfigReadConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_I_CONFIG_READ, data)
        assert isinstance(result, IConfigReadConfig)

    def test_parse_ping_config(self):
        """Test parsing PingConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_PING, data)
        assert isinstance(result, PingConfig)

    def test_parse_rmem_data_write_config(self):
        """Test parsing RMemDataWriteConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_R_MEM_DATA_WRITE, data)
        assert isinstance(result, RMemDataWriteConfig)

    def test_parse_rmem_data_read_config(self):
        """Test parsing RMemDataReadConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_R_MEM_DATA_READ, data)
        assert isinstance(result, RMemDataReadConfig)

    def test_parse_rmem_data_erase_config(self):
        """Test parsing RMemDataEraseConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_R_MEM_DATA_ERASE, data)
        assert isinstance(result, RMemDataEraseConfig)

    def test_parse_random_value_get_config(self):
        """Test parsing RandomValueGetConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_RANDOM_VALUE_GET, data)
        assert isinstance(result, RandomValueGetConfig)

    def test_parse_ecc_key_generate_config(self):
        """Test parsing EccKeyGenerateConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_ECC_KEY_GENERATE, data)
        assert isinstance(result, EccKeyGenerateConfig)

    def test_parse_ecc_key_store_config(self):
        """Test parsing EccKeyStoreConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_ECC_KEY_STORE, data)
        assert isinstance(result, EccKeyStoreConfig)

    def test_parse_ecc_key_read_config(self):
        """Test parsing EccKeyReadConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_ECC_KEY_READ, data)
        assert isinstance(result, EccKeyReadConfig)

    def test_parse_ecc_key_erase_config(self):
        """Test parsing EccKeyEraseConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_ECC_KEY_ERASE, data)
        assert isinstance(result, EccKeyEraseConfig)

    def test_parse_ecdsa_sign_config(self):
        """Test parsing EcdsaSignConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_ECDSA_SIGN, data)
        assert isinstance(result, EcdsaSignConfig)

    def test_parse_eddsa_sign_config(self):
        """Test parsing EddsaSignConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_EDDSA_SIGN, data)
        assert isinstance(result, EddsaSignConfig)

    def test_parse_mcounter_init_config(self):
        """Test parsing MCounterInitConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_MCOUNTER_INIT, data)
        assert isinstance(result, MCounterInitConfig)

    def test_parse_mcounter_get_config(self):
        """Test parsing MCounterGetConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_MCOUNTER_GET, data)
        assert isinstance(result, MCounterGetConfig)

    def test_parse_mcounter_update_config(self):
        """Test parsing MCounterUpdateConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_MCOUNTER_UPDATE, data)
        assert isinstance(result, MCounterUpdateConfig)

    def test_parse_mac_and_destroy_config(self):
        """Test parsing MacAndDestroyConfig."""
        data = b'\x00\x00\x00\x00'
        result = parse_config(CFG_UAP_MAC_AND_DESTROY, data)
        assert isinstance(result, MacAndDestroyConfig)

    def test_parse_unknown_register_raises_error(self):
        """Test that parsing unknown register raises ValueError."""
        data = b'\x00\x00\x00\x00'
        with pytest.raises(ValueError) as exc_info:
            parse_config(0xFFFF, data)  # Invalid register

        assert "Unknown config register" in str(exc_info.value)
