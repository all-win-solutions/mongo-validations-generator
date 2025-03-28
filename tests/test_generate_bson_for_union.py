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

    actual_schema = ItemWithInlineUnion.generate_validation_rules(validation_title)
    assert actual_schema == expected_schema


def test_optional_list_of_union_model_str_bson_generation():
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

    actual_schema = ComplexOptionalList.generate_validation_rules(validation_title)
    assert actual_schema == expected_schema


def test_list_union_with_len_bson_generation():
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

    actual_scheme = ListUnionLen.generate_validation_rules(validation_title)
    assert actual_scheme == expected_schema
