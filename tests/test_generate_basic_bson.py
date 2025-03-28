from typing import Annotated, Any
from mongo_validations_generator import MongoValidator, Long, SchemaIgnored


class BasicMockClass(MongoValidator):
    my_str: str
    my_int: int
    my_float: float
    my_bool: bool
    my_long: Annotated[int, Long]
    my_optional: str | None
    my_hidden_property: Annotated[str, SchemaIgnored]


def test_basic_bson_generation():
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
                "my_optional",
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
                "my_optional": {
                    "oneOf": [{"bsonType": "string"}, {"bsonType": "null"}],
                    "description": "'my_optional' must match schema",
                },
            },
        }
    }

    actual_schema = BasicMockClass.generate_validation_rules(validation_title)
    assert actual_schema == expected_schema
