
class TropicSquareError(Exception):
    """Base exception for all TropicSquare errors"""
    pass


class TropicSquareCRCError(TropicSquareError):
    """CRC validation failed"""
    pass


class TropicSquareNoSession(TropicSquareError):
    """No secure session established"""
    pass


# Communication and protocol errors
class TropicSquareTimeoutError(TropicSquareError):
    """Chip communication timeout"""
    pass


class TropicSquareAlarmError(TropicSquareError):
    """Chip is in alarm state"""
    pass


# Command result errors
class TropicSquareCommandError(TropicSquareError):
    """Base class for command execution errors"""
    pass


class TropicSquareUnauthorizedError(TropicSquareCommandError):
    """Command not authorized"""
    pass


class TropicSquareInvalidCommandError(TropicSquareCommandError):
    """Invalid command"""
    pass


# Memory operation errors
class TropicSquareMemoryError(TropicSquareCommandError):
    """Memory operation error"""
    pass


class TropicSquareMemoryWriteError(TropicSquareMemoryError):
    """Memory write failed"""
    pass


class TropicSquareMemorySlotExpiredError(TropicSquareMemoryError):
    """Memory slot expired"""
    pass


# ECC operation errors
class TropicSquareECCError(TropicSquareCommandError):
    """ECC operation error"""
    pass


class TropicSquareECCInvalidKeyError(TropicSquareECCError):
    """Invalid ECC key"""
    pass


# Counter operation errors
class TropicSquareCounterError(TropicSquareCommandError):
    """Counter operation error"""
    pass


class TropicSquareCounterUpdateError(TropicSquareCounterError):
    """Counter update failed"""
    pass


class TropicSquareCounterInvalidError(TropicSquareCounterError):
    """Invalid counter"""
    pass


# Pairing keys errors
class TropicSquarePairingKeyEmptyError(TropicSquareCommandError):
    """Pairing key empty error"""
    pass


class TropicSquarePairingKeyInvalidError(TropicSquareCommandError):
    """Pairing key invalid error"""
    pass



# Session and handshake errors
class TropicSquareSessionError(TropicSquareError):
    """Session management error"""
    pass


class TropicSquareHandshakeError(TropicSquareSessionError):
    """Handshake failed"""
    pass


class TropicSquareTagError(TropicSquareSessionError):
    """Authentication tag error"""
    pass


class TropicSquareResponseError(TropicSquareError):
    """Response processing error"""
    pass

