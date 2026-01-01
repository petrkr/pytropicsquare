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

# GPO config (CFG_GPO @ 0x14)
# Bit positions from tropic01_application_co.h
GPO_FUNC_MASK = 0x07  # bits 2-0
GPO_FUNC_POS = 0

# Sleep Mode config (CFG_SLEEP_MODE @ 0x18)
# Bit positions from tropic01_application_co.h
SLEEP_MODE_EN_BIT = 0

# UAP (User Access Policy) permission bits
# Each 8-bit field has permission bits for Pairing Key slots 0-3
UAP_PKEY_SLOT_0_BIT = 0
UAP_PKEY_SLOT_1_BIT = 1
UAP_PKEY_SLOT_2_BIT = 2
UAP_PKEY_SLOT_3_BIT = 3
UAP_RESERVED_MASK = 0xF0  # bits 4-7 are reserved

# UAP Pairing Key Write (CFG_UAP_PAIRING_KEY_WRITE @ 0x20)
# 4 slots, each 8 bits
UAP_PKEY_WRITE_SLOT_0_POS = 0
UAP_PKEY_WRITE_SLOT_1_POS = 8
UAP_PKEY_WRITE_SLOT_2_POS = 16
UAP_PKEY_WRITE_SLOT_3_POS = 24
UAP_PKEY_WRITE_SLOT_MASK = 0xFF

# UAP Pairing Key Read (CFG_UAP_PAIRING_KEY_READ @ 0x24)
# Same structure as WRITE
UAP_PKEY_READ_SLOT_0_POS = 0
UAP_PKEY_READ_SLOT_1_POS = 8
UAP_PKEY_READ_SLOT_2_POS = 16
UAP_PKEY_READ_SLOT_3_POS = 24

# UAP Pairing Key Invalidate (CFG_UAP_PAIRING_KEY_INVALIDATE @ 0x28)
# Same structure as WRITE
UAP_PKEY_INVALIDATE_SLOT_0_POS = 0
UAP_PKEY_INVALIDATE_SLOT_1_POS = 8
UAP_PKEY_INVALIDATE_SLOT_2_POS = 16
UAP_PKEY_INVALIDATE_SLOT_3_POS = 24

# UAP MAC and Destroy (CFG_UAP_MAC_AND_DESTROY @ 0x160)
# 4 slots, each 8 bits controlling access to different ranges of MAC-and-Destroy partition
# - slot_0: Access privileges for MAC-and-Destroy slots 0-31
# - slot_1: Access privileges for MAC-and-Destroy slots 32-63
# - slot_2: Access privileges for MAC-and-Destroy slots 64-95
# - slot_3: Access privileges for MAC-and-Destroy slots 96-127
UAP_MACANDD_0_31_POS = 0
UAP_MACANDD_32_63_POS = 8
UAP_MACANDD_64_95_POS = 16
UAP_MACANDD_96_127_POS = 24

# UAP Monotonic Counter (shared by INIT @ 0x150, GET @ 0x154, UPDATE @ 0x158)
# 4 slots, each 8 bits controlling access to different monotonic counters
UAP_MCOUNTER_0_3_POS = 0
UAP_MCOUNTER_4_7_POS = 8
UAP_MCOUNTER_8_11_POS = 16
UAP_MCOUNTER_12_15_POS = 24

# UAP ECC Key operations (shared by GENERATE @ 0x130, STORE @ 0x134, READ @ 0x138,
# ERASE @ 0x13C, ECDSA @ 0x140, EDDSA @ 0x144)
# 4 slots, each 8 bits controlling access to different ECC Key slots
UAP_ECCKEY_SLOT_0_7_POS = 0
UAP_ECCKEY_SLOT_8_15_POS = 8
UAP_ECCKEY_SLOT_16_23_POS = 16
UAP_ECCKEY_SLOT_24_31_POS = 24

# UAP R-MEM User Data operations (shared by WRITE @ 0x110, READ @ 0x114, ERASE @ 0x118)
# 4 slots, each 8 bits controlling access to different User Data slot ranges
UAP_UDATA_SLOT_0_127_POS = 0
UAP_UDATA_SLOT_128_255_POS = 8
UAP_UDATA_SLOT_256_383_POS = 16
UAP_UDATA_SLOT_384_511_POS = 24

# UAP R-CONFIG Write/Erase (CFG_UAP_R_CONFIG_WRITE_ERASE @ 0x30)
# Single 8-bit field
UAP_R_CONFIG_WRITE_ERASE_POS = 0

# UAP R-CONFIG Read (CFG_UAP_R_CONFIG_READ @ 0x34)
# Two 8-bit fields: CFG and FUNC
UAP_R_CONFIG_READ_CFG_POS = 0
UAP_R_CONFIG_READ_FUNC_POS = 8

# UAP I-CONFIG Write (CFG_UAP_I_CONFIG_WRITE @ 0x40)
# Two 8-bit fields: CFG and FUNC
UAP_I_CONFIG_WRITE_CFG_POS = 0
UAP_I_CONFIG_WRITE_FUNC_POS = 8

# UAP I-CONFIG Read (CFG_UAP_I_CONFIG_READ @ 0x44)
# Two 8-bit fields: CFG and FUNC
UAP_I_CONFIG_READ_CFG_POS = 0
UAP_I_CONFIG_READ_FUNC_POS = 8
