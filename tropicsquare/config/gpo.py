"""GPO configuration (CFG_GPO @ 0x14)"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.constants import GPO_FUNC_MASK, GPO_FUNC_POS


class GpoConfig(BaseConfig):
    """General Purpose Output configuration register.

    Controls the function of the GPO pin.

    Fields:
        gpo_func: GPO function selection (bits 2-0, 3-bit value)
    """

    @property
    def gpo_func(self):
        """GPO function selection (3-bit value).

        Returns:
            int: Function code (0-7)
        """
        return (self._value >> GPO_FUNC_POS) & GPO_FUNC_MASK

    @gpo_func.setter
    def gpo_func(self, value):
        """Set GPO function.

        Args:
            value: Function code (0-7)

        Raises:
            ValueError: If value is out of range
        """
        if not 0 <= value <= 7:
            raise ValueError("gpo_func must be 0-7, got {}".format(value))
        # Clear existing bits and set new value
        self._value = (self._value & ~(GPO_FUNC_MASK << GPO_FUNC_POS)) | (value << GPO_FUNC_POS)

    def to_dict(self):
        """Export fields as dictionary.

        Returns:
            dict: Configuration fields and their values
        """
        return {
            'gpo_func': self.gpo_func
        }

    def __str__(self):
        """Human-readable representation."""
        return "GpoConfig(gpo_func={})".format(self.gpo_func)
