from typing import Annotated, Any
from mongo_validations_generator import (
    MongoValidator,
    Long,
    SchemaIgnored,
    BSONDecimal128,
)


class BasicMockClass(MongoValidator):
    my_str: str
    my_int: int
    my_float: float
    my_bool: bool
    my_long: Annotated[int, Long]
    my_decimal: BSONDecimal128
    my_str_optional: str | None
    my_int_optional: int | None
    my_float_optional: float | None
    my_bool_optional: bool | None
    my_long_optional: Annotated[int, Long] | None
    my_decimal_optional: BSONDecimal128 | None
    my_hidden_property: Annotated[str, SchemaIgnored]


def test_basic_bson_generation():
    # Given: A class with basic typed fields and annotated metadata
    validation_title = "Basic"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": [
                "my_str",
                "my_int",
                "my_float",
                "my_bool",
                "my_long",
                "my_decimal",
                "my_str_optional",
                "my_int_optional",
                "my_float_optional",
                "my_bool_optional",
                "my_long_optional",
                "my_decimal_optional",
            ],
            "properties": {
                "my_str": {
                    "bsonType": "string",
                    "description": "'my_str' must match schema",
                },
                "my_int": {
                    "bsonType": "int",
                    "description": "'my_int' must match schema",
                },
                "my_float": {
                    "bsonType": "double",
                    "description": "'my_float' must match schema",
                },
                "my_bool": {
                    "bsonType": "bool",
                    "description": "'my_bool' must match schema",
                },
                "my_long": {
                    "bsonType": "long",
                    "description": "'my_long' must match schema",
                },
                "my_decimal": {
                    "bsonType": "decimal",
                    "description": "'my_decimal' must match schema",
                },
                "my_str_optional": {
                    "oneOf": [{"bsonType": "string"}, {"bsonType": "null"}],
                    "description": "'my_str_optional' must match schema",
                },
                "my_int_optional": {
                    "oneOf": [{"bsonType": "int"}, {"bsonType": "null"}],
                    "description": "'my_int_optional' must match schema",
                },
                "my_float_optional": {
                    "oneOf": [{"bsonType": "double"}, {"bsonType": "null"}],
                    "description": "'my_float_optional' must match schema",
                },
                "my_bool_optional": {
                    "oneOf": [{"bsonType": "bool"}, {"bsonType": "null"}],
                    "description": "'my_bool_optional' must match schema",
                },
                "my_long_optional": {
                    "oneOf": [{"bsonType": "long"}, {"bsonType": "null"}],
                    "description": "'my_long_optional' must match schema",
                },
                "my_decimal_optional": {
                    "oneOf": [{"bsonType": "decimal"}, {"bsonType": "null"}],
                    "description": "'my_decimal_optional' must match schema",
                },
            },
        }
    }

    # When: Generating the BSON validation rules from the class
    actual_schema = BasicMockClass.generate_validation_rules(validation_title)

    # Then: The generated schema should match the expected structure
    assert actual_schema == expected_schema
