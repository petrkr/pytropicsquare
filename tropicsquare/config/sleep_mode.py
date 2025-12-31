"""Sleep Mode configuration (CFG_SLEEP_MODE @ 0x18)"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.constants import SLEEP_MODE_EN_BIT


class SleepModeConfig(BaseConfig):
    """Sleep mode configuration register.

    Controls whether the chip can enter sleep mode.

    Fields:
        sleep_mode_en: Sleep mode enable (bit 0)
    """

    @property
    def sleep_mode_en(self) -> bool:
        """Sleep mode enable flag.

            When True, the chip can enter sleep mode for power saving.
            Default: False (sleep mode disabled)

            :returns: True if sleep mode is enabled
        """
        return bool((self._value >> SLEEP_MODE_EN_BIT) & 1)

    @sleep_mode_en.setter
    def sleep_mode_en(self, value: bool) -> None:
        if value:
            self._value |= (1 << SLEEP_MODE_EN_BIT)
        else:
            self._value &= ~(1 << SLEEP_MODE_EN_BIT)

    def to_dict(self) -> dict:
        """Export fields as dictionary.

            :returns: Configuration fields and their values
        """
        return {
            'sleep_mode_en': self.sleep_mode_en
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        return "SleepModeConfig(sleep_mode_en={})".format(self.sleep_mode_en)
