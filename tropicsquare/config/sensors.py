"""Sensors configuration (CFG_SENSORS @ 0x08)"""

from tropicsquare.config.base import BaseConfig
from tropicsquare.config.constants import (
    SENSORS_PTRNG0_TEST_DIS_BIT,
    SENSORS_PTRNG1_TEST_DIS_BIT,
    SENSORS_OSCMON_DIS_BIT,
    SENSORS_SHIELD_DIS_BIT,
    SENSORS_VMON_DIS_BIT,
    SENSORS_GLITCH_DIS_BIT,
    SENSORS_TEMP_DIS_BIT,
    SENSORS_LASER_DIS_BIT,
    SENSORS_EMP_DIS_BIT,
    SENSORS_CPU_ALERT_DIS_BIT,
    SENSORS_BF_PIN_VER_DIS_BIT,
    SENSORS_BF_SCB_DIS_BIT,
    SENSORS_BF_CPB_DIS_BIT,
    SENSORS_BF_ECC_DIS_BIT,
    SENSORS_BF_RAM_DIS_BIT,
    SENSORS_BF_EKDB_DIS_BIT,
    SENSORS_BF_IMEM_DIS_BIT,
    SENSORS_BF_PLATFORM_DIS_BIT
)


class SensorsConfig(BaseConfig):
    """Sensors and fault detection configuration register.

    Controls security sensors and bit-flip detection mechanisms.
    Each field disables a specific security feature when set to True.

    Fields:

    - ptrng0_test_dis: PTRNG0 test disable (bit 0)
    - ptrng1_test_dis: PTRNG1 test disable (bit 1)
    - oscmon_dis: Oscillator monitoring disable (bit 2)
    - shield_dis: Shield monitoring disable (bit 3)
    - vmon_dis: Voltage monitoring disable (bit 4)
    - glitch_dis: Glitch detection disable (bit 5)
    - temp_dis: Temperature sensor disable (bit 6)
    - laser_dis: Laser detection disable (bit 7)
    - emp_dis: EMP detection disable (bit 8)
    - cpu_alert_dis: CPU alert disable (bit 9)
    - bf_pin_ver_dis: Bit-flip PIN verification disable (bit 10)
    - bf_scb_dis: Bit-flip SCB disable (bit 11)
    - bf_cpb_dis: Bit-flip CPB disable (bit 12)
    - bf_ecc_dis: Bit-flip ECC disable (bit 13)
    - bf_ram_dis: Bit-flip RAM disable (bit 14)
    - bf_ekdb_dis: Bit-flip EKDB disable (bit 15)
    - bf_imem_dis: Bit-flip instruction memory disable (bit 16)
    - bf_platform_dis: Bit-flip platform disable (bit 17)
    """

    def _get_bit(self, bit_pos):
        """Helper to get bit value."""
        return bool((self._value >> bit_pos) & 1)

    def _set_bit(self, bit_pos, value):
        """Helper to set bit value."""
        if value:
            self._value |= (1 << bit_pos)
        else:
            self._value &= ~(1 << bit_pos)

    @property
    def ptrng0_test_dis(self) -> bool:
        """PTRNG0 test disable (bit 0)."""
        return self._get_bit(SENSORS_PTRNG0_TEST_DIS_BIT)

    @ptrng0_test_dis.setter
    def ptrng0_test_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_PTRNG0_TEST_DIS_BIT, value)

    @property
    def ptrng1_test_dis(self) -> bool:
        """PTRNG1 test disable (bit 1)."""
        return self._get_bit(SENSORS_PTRNG1_TEST_DIS_BIT)

    @ptrng1_test_dis.setter
    def ptrng1_test_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_PTRNG1_TEST_DIS_BIT, value)

    @property
    def oscmon_dis(self) -> bool:
        """Oscillator monitoring disable (bit 2)."""
        return self._get_bit(SENSORS_OSCMON_DIS_BIT)

    @oscmon_dis.setter
    def oscmon_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_OSCMON_DIS_BIT, value)

    @property
    def shield_dis(self) -> bool:
        """Shield monitoring disable (bit 3)."""
        return self._get_bit(SENSORS_SHIELD_DIS_BIT)

    @shield_dis.setter
    def shield_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_SHIELD_DIS_BIT, value)

    @property
    def vmon_dis(self) -> bool:
        """Voltage monitoring disable (bit 4)."""
        return self._get_bit(SENSORS_VMON_DIS_BIT)

    @vmon_dis.setter
    def vmon_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_VMON_DIS_BIT, value)

    @property
    def glitch_dis(self) -> bool:
        """Glitch detection disable (bit 5)."""
        return self._get_bit(SENSORS_GLITCH_DIS_BIT)

    @glitch_dis.setter
    def glitch_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_GLITCH_DIS_BIT, value)

    @property
    def temp_dis(self) -> bool:
        """Temperature sensor disable (bit 6)."""
        return self._get_bit(SENSORS_TEMP_DIS_BIT)

    @temp_dis.setter
    def temp_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_TEMP_DIS_BIT, value)

    @property
    def laser_dis(self) -> bool:
        """Laser detection disable (bit 7)."""
        return self._get_bit(SENSORS_LASER_DIS_BIT)

    @laser_dis.setter
    def laser_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_LASER_DIS_BIT, value)

    @property
    def emp_dis(self) -> bool:
        """EMP detection disable (bit 8)."""
        return self._get_bit(SENSORS_EMP_DIS_BIT)

    @emp_dis.setter
    def emp_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_EMP_DIS_BIT, value)

    @property
    def cpu_alert_dis(self) -> bool:
        """CPU alert disable (bit 9)."""
        return self._get_bit(SENSORS_CPU_ALERT_DIS_BIT)

    @cpu_alert_dis.setter
    def cpu_alert_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_CPU_ALERT_DIS_BIT, value)

    @property
    def bf_pin_ver_dis(self) -> bool:
        """Bit-flip PIN verification disable (bit 10)."""
        return self._get_bit(SENSORS_BF_PIN_VER_DIS_BIT)

    @bf_pin_ver_dis.setter
    def bf_pin_ver_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_PIN_VER_DIS_BIT, value)

    @property
    def bf_scb_dis(self) -> bool:
        """Bit-flip SCB disable (bit 11)."""
        return self._get_bit(SENSORS_BF_SCB_DIS_BIT)

    @bf_scb_dis.setter
    def bf_scb_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_SCB_DIS_BIT, value)

    @property
    def bf_cpb_dis(self) -> bool:
        """Bit-flip CPB disable (bit 12)."""
        return self._get_bit(SENSORS_BF_CPB_DIS_BIT)

    @bf_cpb_dis.setter
    def bf_cpb_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_CPB_DIS_BIT, value)

    @property
    def bf_ecc_dis(self) -> bool:
        """Bit-flip ECC disable (bit 13)."""
        return self._get_bit(SENSORS_BF_ECC_DIS_BIT)

    @bf_ecc_dis.setter
    def bf_ecc_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_ECC_DIS_BIT, value)

    @property
    def bf_ram_dis(self) -> bool:
        """Bit-flip RAM disable (bit 14)."""
        return self._get_bit(SENSORS_BF_RAM_DIS_BIT)

    @bf_ram_dis.setter
    def bf_ram_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_RAM_DIS_BIT, value)

    @property
    def bf_ekdb_dis(self) -> bool:
        """Bit-flip EKDB disable (bit 15)."""
        return self._get_bit(SENSORS_BF_EKDB_DIS_BIT)

    @bf_ekdb_dis.setter
    def bf_ekdb_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_EKDB_DIS_BIT, value)

    @property
    def bf_imem_dis(self) -> bool:
        """Bit-flip instruction memory disable (bit 16)."""
        return self._get_bit(SENSORS_BF_IMEM_DIS_BIT)

    @bf_imem_dis.setter
    def bf_imem_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_IMEM_DIS_BIT, value)

    @property
    def bf_platform_dis(self) -> bool:
        """Bit-flip platform disable (bit 17)."""
        return self._get_bit(SENSORS_BF_PLATFORM_DIS_BIT)

    @bf_platform_dis.setter
    def bf_platform_dis(self, value: bool) -> None:
        self._set_bit(SENSORS_BF_PLATFORM_DIS_BIT, value)

    def to_dict(self) -> dict:
        """Export fields as dictionary.

            :returns: Configuration fields and their values
            :rtype: dict
        """
        return {
            'ptrng0_test_dis': self.ptrng0_test_dis,
            'ptrng1_test_dis': self.ptrng1_test_dis,
            'oscmon_dis': self.oscmon_dis,
            'shield_dis': self.shield_dis,
            'vmon_dis': self.vmon_dis,
            'glitch_dis': self.glitch_dis,
            'temp_dis': self.temp_dis,
            'laser_dis': self.laser_dis,
            'emp_dis': self.emp_dis,
            'cpu_alert_dis': self.cpu_alert_dis,
            'bf_pin_ver_dis': self.bf_pin_ver_dis,
            'bf_scb_dis': self.bf_scb_dis,
            'bf_cpb_dis': self.bf_cpb_dis,
            'bf_ecc_dis': self.bf_ecc_dis,
            'bf_ram_dis': self.bf_ram_dis,
            'bf_ekdb_dis': self.bf_ekdb_dis,
            'bf_imem_dis': self.bf_imem_dis,
            'bf_platform_dis': self.bf_platform_dis
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        fields = self.to_dict()
        enabled_sensors = [k for k, v in fields.items() if not v]
        disabled_sensors = [k for k, v in fields.items() if v]
        return "SensorsConfig({} enabled, {} disabled)".format(
            len(enabled_sensors), len(disabled_sensors))
