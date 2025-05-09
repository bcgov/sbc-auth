"""Serializable class for cattr structure and unstructure."""

from auth_api.utils.converter import Converter


class Serializable:
    """Helper for cattr structure and unstructure (serialization/deserialization)."""

    @classmethod
    def from_dict(cls, data: dict):
        """Convert from dictionary to object."""
        return Converter(camel_to_snake_case=True).structure(data, cls)

    def to_dict(self):
        """Convert from object to dictionary."""
        return Converter(snake_case_to_camel=True).unstructure(self)
