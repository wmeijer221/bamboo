class BambooException(Exception):
    """Base Bamboo exception.

    This exception is raised for generic Bamboo validation and transformation
    failures. All Bamboo-specific exceptions inherit from this base class.
    """


class BambooInputException(BambooException):
    """Raised when input data fails Bamboo validation."""


class BambooOutputException(BambooException):
    """Raised when output data fails Bamboo validation."""


class BambooTransformationException(BambooException):
    """Raised when a Bamboo transformation itself raises an exception."""
