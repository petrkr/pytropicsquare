"""
Error code to exception mapping for TropicSquare
"""

from tropicsquare.exceptions import *
from tropicsquare.constants.cmd_result import *
from tropicsquare.constants.rsp_status import *


def map_cmd_result_to_exception(cmd_result):
    """Map command result code to appropriate exception"""
    error_map = {
        CMD_RESULT_FAIL: (TropicSquareCommandError, "Command execution failed"),
        CMD_RESULT_UNAUTHORIZED: (TropicSquareUnauthorizedError, "Command not authorized"),
        CMD_RESULT_INVALID_CMD: (TropicSquareInvalidCommandError, "Invalid command"),
        CMD_RESULT_MEM_WRITE_FAIL: (TropicSquareMemoryWriteError, "Memory write operation failed"),
        CMD_RESULT_MEM_SLOT_EXPIRED: (TropicSquareMemorySlotExpiredError, "Memory slot has expired"),
        CMD_RESULT_ECC_INVALID_KEY: (TropicSquareECCInvalidKeyError, "ECC key is invalid or not found"),
        CMD_RESULT_MCOUNTER_UPDATE_ERROR: (TropicSquareCounterUpdateError, "Monotonic counter update failed"),
        CMD_RESULT_MCOUNTER_COUNTER_INVALID: (TropicSquareCounterInvalidError, "Invalid monotonic counter"),
        CMD_RESULT_PAIRING_KEY_EMPTY: (TropicSquarePairingKeyEmptyError, "Pairing key slot is empty"),
        CMD_RESULT_PAIRING_KEY_INVALID: (TropicSquarePairingKeyInvalidError, "Invalid pairing key"),
    }
    
    exception_class, message = error_map.get(cmd_result, (TropicSquareCommandError, "Command failed"))
    return exception_class(f"{message} (result: {hex(cmd_result)})")


def map_response_status_to_exception(rsp_status):
    """Map response status code to appropriate exception"""
    error_map = {
        RSP_STATUS_RESP_DISABLED: (TropicSquareResponseError, "Response disabled"),
        RSP_STATUS_HSK_ERROR: (TropicSquareHandshakeError, "Handshake error"),
        RSP_STATUS_NO_SESSION: (TropicSquareNoSession, "No secure session established"),
        RSP_STATUS_TAG_ERROR: (TropicSquareTagError, "Authentication tag error"),
        RSP_STATUS_CRC_ERROR: (TropicSquareCRCError, "CRC validation failed"),
        RSP_STATUS_UNKNOWN_REQ: (TropicSquareInvalidCommandError, "Unknown request"),
        RSP_STATUS_GEN_ERROR: (TropicSquareError, "General error"),
        RSP_STATUS_NO_RESPONSE: (TropicSquareTimeoutError, "No response from chip"),
    }
    
    exception_class, message = error_map.get(rsp_status, (TropicSquareError, "Unknown response error"))
    return exception_class(f"{message} (status: {hex(rsp_status)})")


def raise_for_cmd_result(cmd_result):
    """Raise exception if command result indicates error"""
    if cmd_result != CMD_RESULT_OK:
        raise map_cmd_result_to_exception(cmd_result)


def raise_for_response_status(rsp_status):
    """Raise exception if response status indicates error"""
    valid_statuses = [RSP_STATUS_REQ_OK, RSP_STATUS_RES_OK, RSP_STATUS_RES_CONT, RSP_STATUS_REQ_CONT]
    if rsp_status not in valid_statuses:
        raise map_response_status_to_exception(rsp_status)