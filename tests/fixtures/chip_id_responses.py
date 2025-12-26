"""Real hardware response data for test fixtures.

This module contains actual responses captured from TROPIC01 hardware 
from 2025-12-26.

These fixtures are used in unit tests to ensure realistic test coverage
without requiring hardware access during CI/CD.
"""

# Chip ID response (128 bytes) - captured via get_info_req(GET_INFO_CHIPID)
CHIP_ID_SAMPLE = bytes.fromhex(
    "010000000000000000000000000000000000000001000000000000ff41434142"
    "80aaffff01001101085b0006050100000000ffff02001101085b1905090d0000"
    "0000046f0d545230312d4332502d54313031ffff0104d8966128000c7deda870"
    "1905090d00ffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)

# X.509 Certificate response (128 bytes, first chunk) - captured via get_info_req(GET_INFO_X509_CERT)
CERTIFICATE_SAMPLE = bytes.fromhex(
    "010401d20262028f025c308201ce30820155a003020102021002001101085b19"
    "05090d00000000046f300a06082a8648ce3d0403033047310b30090603550406"
    "1302435a311d301b060355040a0c1454726f7069632053717561726520732e72"
    "2e6f2e3119301706035504030c1054524f50494330312d54204341207631301e"
)

# Serial number is embedded in CHIP_ID_SAMPLE at specific offset
# Can be extracted using SerialNumber class for separate testing
