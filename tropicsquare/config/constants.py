"""Internal bit positions and masks for config fields

These constants are used internally by config classes to access
individual configuration bits. Not intended for public API use.
"""

# StartUp config (CFG_START_UP @ 0x00)
# Bit positions from tropic01_bootloader_co.h
STARTUP_MBIST_DIS_BIT = 1
STARTUP_RNGTEST_DIS_BIT = 2
STARTUP_MAINTENANCE_ENA_BIT = 3

# Sensors config (CFG_SENSORS @ 0x08)
# Bit positions from tropic01_bootloader_co.h
SENSORS_PTRNG0_TEST_DIS_BIT = 0
SENSORS_PTRNG1_TEST_DIS_BIT = 1
SENSORS_OSCMON_DIS_BIT = 2
SENSORS_SHIELD_DIS_BIT = 3
SENSORS_VMON_DIS_BIT = 4
SENSORS_GLITCH_DIS_BIT = 5
SENSORS_TEMP_DIS_BIT = 6
SENSORS_LASER_DIS_BIT = 7
SENSORS_EMP_DIS_BIT = 8
SENSORS_CPU_ALERT_DIS_BIT = 9
SENSORS_BF_PIN_VER_DIS_BIT = 10
SENSORS_BF_SCB_DIS_BIT = 11
SENSORS_BF_CPB_DIS_BIT = 12
SENSORS_BF_ECC_DIS_BIT = 13
SENSORS_BF_RAM_DIS_BIT = 14
SENSORS_BF_EKDB_DIS_BIT = 15
SENSORS_BF_IMEM_DIS_BIT = 16
SENSORS_BF_PLATFORM_DIS_BIT = 17

# Debug config (CFG_DEBUG @ 0x10)
# Bit positions from tropic01_bootloader_co.h
DEBUG_FW_LOG_EN_BIT = 0
