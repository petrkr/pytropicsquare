"""Configuration objects for TROPIC01 secure element

This module provides classes for parsing and manipulating TROPIC01
configuration registers. Configuration is split into two memory spaces:

- R-CONFIG (Reversible): Can be written and erased freely
- I-CONFIG (Irreversible): Bits can only change from 1 to 0 permanently

The effective configuration is the AND of R-CONFIG and I-CONFIG values.

Usage:
    from tropicsquare import TropicSquareCPython
    from tropicsquare.constants.config import CFG_START_UP
    from tropicsquare.config import parse_config

    ts = TropicSquareCPython(...)
    ts.establish_session()

    # Read R-CONFIG startup register
    data = ts.r_config_read(CFG_START_UP)
    config = parse_config(CFG_START_UP, data)
    print(config.mbist_dis)

    # Read I-CONFIG and compute effective value
    r_data = ts.r_config_read(CFG_START_UP)
    i_data = ts.i_config_read(CFG_START_UP)
    r_config = parse_config(CFG_START_UP, r_data)
    i_config = parse_config(CFG_START_UP, i_data)
    effective = StartUpConfig(r_config._value & i_config._value)
"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.startup import StartUpConfig
from tropicsquare.config.sensors import SensorsConfig
from tropicsquare.config.debug import DebugConfig

from tropicsquare.constants.config import (
    CFG_START_UP,
    CFG_SENSORS,
    CFG_DEBUG
)


def parse_config(register, data):
    """Parse config data into appropriate Config object.

    Factory function that creates the correct config object type
    based on the register address.

    Args:
        register: Registry address (use CFG_* constants from tropicsquare.constants.config)
        data: 4 bytes from r_config_read() or i_config_read()

    Returns:
        BaseConfig: Appropriate config object (StartUpConfig, SensorsConfig, etc.)

    Raises:
        ValueError: If register address is unknown

    Example:
        from tropicsquare.constants.config import CFG_START_UP
        from tropicsquare.config import parse_config

        data = ts.r_config_read(CFG_START_UP)
        config = parse_config(CFG_START_UP, data)
        print(config.mbist_dis)
    """
    if register == CFG_START_UP:
        return StartUpConfig.from_bytes(data)
    elif register == CFG_SENSORS:
        return SensorsConfig.from_bytes(data)
    elif register == CFG_DEBUG:
        return DebugConfig.from_bytes(data)
    else:
        raise ValueError("Unknown config register: 0x{:02x}".format(register))
