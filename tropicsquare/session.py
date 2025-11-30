"""
Session management utilities for TropicSquare
"""

from .exceptions import TropicSquareError


class SecureSession:
    """Context manager for secure sessions with automatic cleanup
    
    TROPIC01 supports only one active session at a time.
    
    Usage:
        with SecureSession(chip, key_index, private_key, public_key) as secure_chip:
            result = secure_chip.ping(b"test")
            # session automatically cleaned up on exit
    """
    
    _active_session = None  # Class variable to track active session
    
    def __init__(self, chip, key_index, private_key, public_key):
        """Initialize session manager
        
        Args:
            chip: TropicSquare chip instance
            key_index: Pairing key index
            private_key: Pairing private key (bytes)
            public_key: Pairing public key (bytes)
        """
        self.chip = chip
        self.key_index = key_index
        self.private_key = private_key
        self.public_key = public_key
        self._session_active = False
    
    def __enter__(self):
        """Start secure session"""
        if SecureSession._active_session is not None:
            raise TropicSquareError("Another secure session is already active")
        
        try:
            self.chip.start_secure_session(self.key_index, self.private_key, self.public_key)
            self._session_active = True
            SecureSession._active_session = self
            return self.chip
        except Exception as e:
            # If session start fails, make sure we don't try to clean up
            self._session_active = False
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up session on exit"""
        if self._session_active:
            try:
                self.chip.abort_secure_session()
            except Exception:
                # Ignore cleanup errors - don't mask original exception
                pass
            finally:
                self._session_active = False
                SecureSession._active_session = None
        
        # Don't suppress any exceptions
        return False
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        return self._session_active


