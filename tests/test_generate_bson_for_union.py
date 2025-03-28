from typing import Annotated, Any, List, Optional, Union

from annotated_types import Len
from mongo_validations_generator import MongoValidator


class MyMockClass(MongoValidator):
    id: str


class ItemWithInlineUnion(MongoValidator):
    data: list[MyMockClass | int]


class ComplexOptionalList(MongoValidator):
    entries: Optional[List[Union[MyMockClass, str]]]


class ListUnionLen(MongoValidator):
    data: Annotated[List[Union[int, str]], Len(1, 3)]


expected_my_mock_class_bson_schema: dict[str, Any] = {
    "bsonType": "object",
    "required": ["id"],
    "properties": {
        "id": {
            "bsonType": "string",
            "description": "'id' must match schema",
        }
    },
}


def test_uniontype_inside_list_bson_generation():
    # Given: A class with a list of items that can be either a model or an integer
    validation_title = "List of Model or Int"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["data"],
            "properties": {
                "data": {
                    "bsonType": "array",
                    "items": {
                        "oneOf": [
                            expected_my_mock_class_bson_schema,
                            {"bsonType": "int"},
                        ]
                    },
                    "description": "'data' must match schema",
                }
            },
        }
    }

    # When: Generating BSON validation rules
    actual_schema = ItemWithInlineUnion.generate_validation_rules(validation_title)

    # Then: The result should support both models and integers in the list
    assert actual_schema == expected_schema


def test_optional_list_of_union_model_str_bson_generation():
    # Given: A class with an optional list containing either a model or a string
    validation_title = "Optional List of Union Model or Str"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["entries"],
            "properties": {
                "entries": {
                    "oneOf": [
                        {
                            "bsonType": "array",
                            "items": {
                                "oneOf": [
                                    expected_my_mock_class_bson_schema,
                                    {"bsonType": "string"},
                                ]
                            },
                        },
                        {"bsonType": "null"},
                    ],
                    "description": "'entries' must match schema",
                }
            },
        }
    }

    # When: Generating BSON schema for optional union list
    actual_schema = ComplexOptionalList.generate_validation_rules(validation_title)

    # Then: The result should allow model or string items, or null
    assert actual_schema == expected_schema


def test_list_union_with_len_bson_generation():
    # Given: A list of int or str with length constraints
    validation_title = "List of Union With Len"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["data"],
            "properties": {
                "data": {
                    "bsonType": "array",
                    "items": {"oneOf": [{"bsonType": "int"}, {"bsonType": "string"}]},
                    "minItems": 1,
                    "maxItems": 3,
                    "description": "'data' must match schema",
                }
            },
        }
    }

    # When: Generating schema with union type and length constraints
    actual_scheme = ListUnionLen.generate_validation_rules(validation_title)

    # Then: The generated schema must reflect both union and length
    assert actual_scheme == expected_schema
