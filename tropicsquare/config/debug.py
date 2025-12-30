"""Debug configuration (CFG_DEBUG @ 0x10)"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.constants import DEBUG_FW_LOG_EN_BIT


class DebugConfig(BaseConfig):
    """Debug configuration register.

    Controls debugging features and logging.

    Fields:
        fw_log_en: Firmware logging enable (bit 0)
    """

    @property
    def fw_log_en(self) -> bool:
        """Firmware logging enable flag.

        When True, firmware logging is enabled. Logs can be retrieved
        using appropriate debug commands.
        Default: False (logging disabled)

            :returns: True if firmware logging is enabled
            :rtype: bool
        """
        return bool((self._value >> DEBUG_FW_LOG_EN_BIT) & 1)

    @fw_log_en.setter
    def fw_log_en(self, value: bool) -> None:
        if value:
            self._value |= (1 << DEBUG_FW_LOG_EN_BIT)
        else:
            self._value &= ~(1 << DEBUG_FW_LOG_EN_BIT)

    def to_dict(self) -> dict:
        """Export fields as dictionary.

            :returns: Configuration fields and their values
            :rtype: dict
        """
        return {
            'fw_log_en': self.fw_log_en
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        return "DebugConfig(fw_log_en={})".format(self.fw_log_en)
