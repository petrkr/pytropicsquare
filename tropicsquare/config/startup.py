"""Startup configuration (CFG_START_UP @ 0x00)"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.constants import (
    STARTUP_MBIST_DIS_BIT,
    STARTUP_RNGTEST_DIS_BIT,
    STARTUP_MAINTENANCE_ENA_BIT
)


class StartUpConfig(BaseConfig):
    """Startup configuration register.

    Controls bootloader behavior including built-in self-tests
    and maintenance mode.

    Fields:
        mbist_dis: Memory built-in self-test disable (bit 1)
        rngtest_dis: Random number generator test disable (bit 2)
        maintenance_ena: Maintenance mode enable (bit 3)
    """

    @property
    def mbist_dis(self) -> bool:
        """Memory BIST disable flag.

            When True, memory built-in self-test is disabled during startup.
            Default: False (BIST enabled)

            :returns: True if MBIST is disabled
        """
        return bool((self._value >> STARTUP_MBIST_DIS_BIT) & 1)

    @mbist_dis.setter
    def mbist_dis(self, value: bool) -> None:
        if value:
            self._value |= (1 << STARTUP_MBIST_DIS_BIT)
        else:
            self._value &= ~(1 << STARTUP_MBIST_DIS_BIT)

    @property
    def rngtest_dis(self) -> bool:
        """RNG test disable flag.

            When True, random number generator test is disabled during startup.
            Default: False (RNG test enabled)

            :returns: True if RNG test is disabled
        """
        return bool((self._value >> STARTUP_RNGTEST_DIS_BIT) & 1)

    @rngtest_dis.setter
    def rngtest_dis(self, value: bool) -> None:
        if value:
            self._value |= (1 << STARTUP_RNGTEST_DIS_BIT)
        else:
            self._value &= ~(1 << STARTUP_RNGTEST_DIS_BIT)

    @property
    def maintenance_ena(self) -> bool:
        """Maintenance mode enable flag.

            When True, chip boots into maintenance mode instead of
            normal application mode.
            Default: False (normal boot)

            :returns: True if maintenance mode is enabled
        """
        return bool((self._value >> STARTUP_MAINTENANCE_ENA_BIT) & 1)

    @maintenance_ena.setter
    def maintenance_ena(self, value: bool) -> None:
        if value:
            self._value |= (1 << STARTUP_MAINTENANCE_ENA_BIT)
        else:
            self._value &= ~(1 << STARTUP_MAINTENANCE_ENA_BIT)

    def to_dict(self) -> dict:
        """Export fields as dictionary.

            :returns: Configuration fields and their values
        """
        return {
            'mbist_dis': self.mbist_dis,
            'rngtest_dis': self.rngtest_dis,
            'maintenance_ena': self.maintenance_ena
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        return "StartUpConfig(mbist_dis={}, rngtest_dis={}, maintenance_ena={})".format(
            self.mbist_dis, self.rngtest_dis, self.maintenance_ena)
