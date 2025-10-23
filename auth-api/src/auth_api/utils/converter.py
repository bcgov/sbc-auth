"""Converter module to support attrs and data class serialization."""

import dataclasses
import re
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

import cattrs
from attrs import fields as attrs_fields
from attrs import has as attrs_has
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override


class Converter(cattrs.Converter):
    """Enhanced cattrs converter for camelCase/snake_case and special types."""

    def __init__(
        self,
        camel_to_snake_case: bool = False,
        snake_case_to_camel: bool = False,
        enum_to_value: bool = False,
    ):
        """Initialize the converter with configuration options."""
        super().__init__()

        self.register_structure_hook(Decimal, self._structure_decimal)
        self.register_unstructure_hook(Decimal, self._unstructure_decimal)
        self.register_unstructure_hook(datetime, self._unstructure_datetime)
        if enum_to_value:
            self.register_structure_hook(Enum, self._structure_enum_value)

        def register_case_hooks(type_check, field_getter):
            if snake_case_to_camel:
                self.register_unstructure_hook_factory(
                    type_check, self._make_case_unstructure(field_getter, self._to_camel_case)
                )
                self.register_structure_hook_factory(
                    type_check, self._make_case_structure(field_getter, self._to_snake_case)
                )

            if camel_to_snake_case:
                self.register_unstructure_hook_factory(
                    type_check, self._make_case_unstructure(field_getter, self._to_snake_case)
                )
                self.register_structure_hook_factory(
                    type_check, self._make_case_structure(field_getter, self._to_camel_case)
                )

        # Register for both attrs and dataclasses
        register_case_hooks(attrs_has, attrs_fields)
        register_case_hooks(dataclasses.is_dataclass, dataclasses.fields)

    @staticmethod
    def _make_case_unstructure(field_getter, rename_func):
        def unstructure(cls):
            return make_dict_unstructure_fn(
                cls, Converter(), **{f.name: override(rename=rename_func(f.name)) for f in field_getter(cls)}
            )

        return unstructure

    @staticmethod
    def _make_case_structure(field_getter, rename_func):
        def structure(cls):
            return make_dict_structure_fn(
                cls, Converter(), **{f.name: override(rename=rename_func(f.name)) for f in field_getter(cls)}
            )

        return structure

    @staticmethod
    def _to_snake_case(camel_str: str) -> str:
        """Convert camelCase or PascalCase to snake_case."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()

    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    @staticmethod
    def _structure_decimal(obj: Any, cls: type) -> Decimal:
        return cls(str(obj))

    @staticmethod
    def _structure_enum_value(obj: Any, cls: type):
        if not issubclass(cls, Enum):
            return None
        return obj

    @staticmethod
    def _unstructure_decimal(obj: Decimal) -> float:
        return float(obj or 0)

    @staticmethod
    def _unstructure_datetime(obj: datetime) -> str:
        return obj.isoformat() if obj else None

    @staticmethod
    def remove_nones(data: dict[Any, Any]) -> dict[str, Any]:
        """Remove keys with None values from a dictionary, recursively."""
        new_data = {}
        for key, val in data.items():
            if isinstance(val, dict):
                new_data[key] = Converter.remove_nones(val)
            elif val is not None:
                new_data[key] = val
        return new_data
