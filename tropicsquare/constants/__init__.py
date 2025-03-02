

# Format [Request ID, Optional request Length]
# L2 Request IDs

REQ_ID_GET_INFO_REQ = [0x01, 0x02]
REQ_ID_HANDSHARE_REQ = [0x02, 0x21]
REQ_ID_ENCRYPTED_CMD_REQ = [0x04] # Dynamic length, send from API
REQ_ID_ENCRYPTED_SESSION_ABT = [0x08, 0x00]
REQ_ID_RESEND_REQ = [0x10, 0x00]
REQ_ID_SLEEP_REQ = [0x20, 0x01]
REQ_ID_STARTUP_REQ = [0xB3, 0x01]
REQ_ID_GET_LOG_REQ = [0xA2, 0x00]

REQ_ID_GET_RESPONSE = [0xAA] # Does not send length


PROTOCOL_NAME = b'Noise_KK1_25519_AESGCM_SHA256\x00\x00\x00'

COMMAND_SIZE_LEN = 2
CFG_ADDRESS_SIZE = 2
MEM_ADDRESS_SIZE = 2
MEM_DATA_MAX_SIZE = 444

# Format [Optional command Length, Command ID]
# L3 Command IDs
CMD_ID_PING = 0x01

CMD_ID_PAIRING_KEY_WRITE = 0x10
CMD_ID_PAIRING_KEY_READ = 0x11
# CMD_ID_PAIRING_KEY_INVALIDATE = [0x03, 0x12] # For debug safe, do not support this yet

# CMD_ID_R_CFG_WRITE = [0x08, 0x20] # For debug safe, do not support this yet
CMD_ID_R_CFG_READ = 0x21
# CMD_ID_R_CFG_ERASE = [0x01, 0x22] # For debug safe, do not support this yet

# CMD_ID_I_CFG_WRITE = [0x04, 0x30] # For debug safe, do not support this yet
CMD_ID_I_CFG_READ = 0x31

CMD_ID_R_MEMDATA_WRITE = 0x40
CMD_ID_R_MEMDATA_READ = 0x41
CMD_ID_R_MEMDATA_ERASE = 0x42

CMD_ID_RANDOM_VALUE = 0x50

CMD_ECC_KEY_GENERATE = 0x60

CMD_ID_SERIAL_CODE_GET = 0xA0
