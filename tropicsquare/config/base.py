"""Base configuration class for TROPIC01 config objects"""


class BaseConfig:
    """Base class for all configuration objects.

    Configuration objects represent 32-bit hardware registers that control
    various aspects of TROPIC01 operation. Each config object provides
    bit-level access to individual configuration fields.

    Default value is 0xFFFFFFFF (all bits set) to prevent accidental
    erasure of I-CONFIG memory, where bits can only be changed from 1 to 0
    (irreversible operation).

    Attributes:
        _value: 32-bit integer holding the raw configuration value
    """

    def __init__(self, value: int = 0xFFFFFFFF) -> None:
        """Initialize config object.

            :param value: 32-bit configuration value (default: 0xFFFFFFFF)
        """
        self._value = value

    @classmethod
    def from_bytes(cls, data: bytes) -> 'BaseConfig':
        """Create config object from raw bytes.

            :param data: 4 bytes in big-endian format

            :returns: New config object instance

            :raises ValueError: If data is not exactly 4 bytes
        """
        if len(data) != 4:
            raise ValueError("Expected 4 bytes, got {}".format(len(data)))
        value = int.from_bytes(data, 'big')
        return cls(value)

    def to_bytes(self) -> bytes:
        """Convert config object to raw bytes.

            :returns: 4 bytes in big-endian format
        """
        return self._value.to_bytes(4, 'big')

    def to_dict(self) -> dict:
        """Export configuration fields as dictionary.

            :returns: Dictionary mapping field names to values
            :rtype: dict

            :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement to_dict()")

    def __repr__(self) -> str:
        """Machine-readable representation."""
        return "{}(0x{:08x})".format(self.__class__.__name__, self._value)

    def __str__(self) -> str:
        """Human-readable representation.

        Default implementation shows class name and hex value.
        Subclasses should override for more detailed output.
        """
        return "{}(0x{:08x})".format(self.__class__.__name__, self._value)
