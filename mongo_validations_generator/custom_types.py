from decimal import Decimal
from typing import Any, Sequence, Tuple, Union
from bson import Decimal128
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import (
    CoreSchema,
    json_or_python_schema,
    no_info_plain_validator_function,
    plain_serializer_function_ser_schema,
)


_DecimalConvertible = Union[Decimal, str, Tuple[int, Sequence[int], int]]


class Long:
    pass


class SchemaIgnored:
    pass


class BSONDecimal128:
    def __init__(self, value: Decimal128 | _DecimalConvertible):
        try:
            if isinstance(value, Decimal128):
                self.value = value
            else:
                self.value = Decimal128(value)
        except Exception:
            raise PydanticCustomError(
                "bson_decimal_conversion",
                'Cannot convert value "{value}" to BSON Decimal128',
                {"value": value},
            )

    def __repr__(self) -> str:
        return f"BSONDecimal128({str(self)})"

    def __str__(self) -> str:
        return str(self.value)

    def to_decimal(self) -> Decimal:
        return self.value.to_decimal()

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        schema = no_info_plain_validator_function(cls.__validate)

        return json_or_python_schema(
            json_schema=schema,
            python_schema=schema,
            serialization=plain_serializer_function_ser_schema(
                lambda value: value.to_decimal(),
                when_used="json",
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> dict[str, Any]:
        return {
            "type": "string",
            "format": "decimal128",
            "description": "MongoDB Decimal128 compatible value",
        }

    @classmethod
    def __validate(cls, input_value: Any) -> Decimal128:
        if isinstance(input_value, cls):
            return input_value.value

        return cls(input_value).value
