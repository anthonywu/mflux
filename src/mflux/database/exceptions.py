"""Exceptions for database operations."""

class LoRAProfileError(Exception):
    """Base exception for LoRA profile operations."""
    pass


class ProfileNotFoundError(LoRAProfileError):
    """Raised when a profile with the specified name is not found."""
    pass


class ProfileExistsError(LoRAProfileError):
    """Raised when trying to create a profile with a name that already exists."""
    pass


class EntryValidationError(LoRAProfileError):
    """Raised when a LoRA entry fails validation."""
    pass


class EntryIndexError(LoRAProfileError):
    """Raised when an invalid entry index is provided."""
    pass