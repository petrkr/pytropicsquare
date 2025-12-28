"""Configuration objects for TROPIC01 secure element

This module provides classes for parsing and manipulating TROPIC01
configuration registers. Configuration is split into two memory spaces:

- R-CONFIG (Reversible): Can be written and erased freely
- I-CONFIG (Irreversible): Bits can only change from 1 to 0 permanently

The effective configuration is the AND of R-CONFIG and I-CONFIG values.

Usage:
    from tropicsquare import TropicSquareCPython
    from tropicsquare.constants.config import CFG_START_UP
    from tropicsquare.config.startup import StartUpConfig

    ts = TropicSquareCPython(...)
    ts.establish_session()

    # Read R-CONFIG startup register (auto-parsed)
    config = ts.r_config_read(CFG_START_UP)
    print(config.mbist_dis)

    # Read I-CONFIG and compute effective value
    r_config = ts.r_config_read(CFG_START_UP)
    i_config = ts.i_config_read(CFG_START_UP)
    effective = StartUpConfig(r_config._value & i_config._value)
"""

from tropicsquare.config.base import BaseConfig
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


def parse_config(register, data):
    """Parse config data into appropriate Config object.

    Factory function that creates the correct config object type
    based on the register address.

    Note: This function is used internally by r_config_read() and i_config_read().
    You typically don't need to call this directly as those methods return
    already-parsed config objects.

    Args:
        register: Registry address (use CFG_* constants from tropicsquare.constants.config)
        data: 4 bytes of raw config data

    Returns:
        BaseConfig: Appropriate config object (StartUpConfig, SensorsConfig, etc.)

    Raises:
        ValueError: If register address is unknown

    Example (advanced usage with raw bytes):
        from tropicsquare.constants.config import CFG_START_UP
        from tropicsquare.config import parse_config

        raw_data = b'\\x12\\x34\\x56\\x78'
        config = parse_config(CFG_START_UP, raw_data)
        print(config.mbist_dis)
    """
    if register == CFG_START_UP:
        return StartUpConfig.from_bytes(data)
    elif register == CFG_SENSORS:
        return SensorsConfig.from_bytes(data)
    elif register == CFG_DEBUG:
        return DebugConfig.from_bytes(data)
    elif register == CFG_GPO:
        return GpoConfig.from_bytes(data)
    elif register == CFG_SLEEP_MODE:
        return SleepModeConfig.from_bytes(data)
    elif register == CFG_UAP_PAIRING_KEY_WRITE:
        return PairingKeyWriteConfig.from_bytes(data)
    elif register == CFG_UAP_PAIRING_KEY_READ:
        return PairingKeyReadConfig.from_bytes(data)
    elif register == CFG_UAP_PAIRING_KEY_INVALIDATE:
        return PairingKeyInvalidateConfig.from_bytes(data)
    elif register == CFG_UAP_R_CONFIG_WRITE_ERASE:
        return RConfigWriteEraseConfig.from_bytes(data)
    elif register == CFG_UAP_R_CONFIG_READ:
        return RConfigReadConfig.from_bytes(data)
    elif register == CFG_UAP_I_CONFIG_WRITE:
        return IConfigWriteConfig.from_bytes(data)
    elif register == CFG_UAP_I_CONFIG_READ:
        return IConfigReadConfig.from_bytes(data)
    elif register == CFG_UAP_PING:
        return PingConfig.from_bytes(data)
    elif register == CFG_UAP_R_MEM_DATA_WRITE:
        return RMemDataWriteConfig.from_bytes(data)
    elif register == CFG_UAP_R_MEM_DATA_READ:
        return RMemDataReadConfig.from_bytes(data)
    elif register == CFG_UAP_R_MEM_DATA_ERASE:
        return RMemDataEraseConfig.from_bytes(data)
    elif register == CFG_UAP_RANDOM_VALUE_GET:
        return RandomValueGetConfig.from_bytes(data)
    elif register == CFG_UAP_ECC_KEY_GENERATE:
        return EccKeyGenerateConfig.from_bytes(data)
    elif register == CFG_UAP_ECC_KEY_STORE:
        return EccKeyStoreConfig.from_bytes(data)
    elif register == CFG_UAP_ECC_KEY_READ:
        return EccKeyReadConfig.from_bytes(data)
    elif register == CFG_UAP_ECC_KEY_ERASE:
        return EccKeyEraseConfig.from_bytes(data)
    elif register == CFG_UAP_ECDSA_SIGN:
        return EcdsaSignConfig.from_bytes(data)
    elif register == CFG_UAP_EDDSA_SIGN:
        return EddsaSignConfig.from_bytes(data)
    elif register == CFG_UAP_MCOUNTER_INIT:
        return MCounterInitConfig.from_bytes(data)
    elif register == CFG_UAP_MCOUNTER_GET:
        return MCounterGetConfig.from_bytes(data)
    elif register == CFG_UAP_MCOUNTER_UPDATE:
        return MCounterUpdateConfig.from_bytes(data)
    elif register == CFG_UAP_MAC_AND_DESTROY:
        return MacAndDestroyConfig.from_bytes(data)
    else:
        raise ValueError("Unknown config register: 0x{:02x}".format(register))
