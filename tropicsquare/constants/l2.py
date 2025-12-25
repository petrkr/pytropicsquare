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

MAX_RETRIES = 10

# L3 Command size length
COMMAND_SIZE_LEN = 2
