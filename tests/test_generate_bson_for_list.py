from typing import Annotated, Any, List, Literal, Optional

from annotated_types import Len
from mongo_validations_generator import MongoValidator


class MockClass(MongoValidator):
    my_str_list: list[str]
    my_int_list: list[int]
    my_float_list: list[float]
    my_optional_list: list[str] | None
    my_int_or_bool_list: list[int | bool]


class MyMockListClass(MongoValidator):
    my_mock_class_list: list[MockClass]


class ListWithoutType(MongoValidator):
    generic_list: list  # type: ignore


class ListWithLen(MongoValidator):
    fixed_list: Annotated[list[int], Len(2, 5)]


class ListWithLiteral(MongoValidator):
    state_list: list[Literal["on", "off"]]


class NestedList(MongoValidator):
    matrix: list[list[int]]


expected_mock_class_bson_schema: dict[str, Any] = {
    "bsonType": "object",
    "required": [
        "my_str_list",
        "my_int_list",
        "my_float_list",
        "my_optional_list",
        "my_int_or_bool_list",
    ],
    "properties": {
        "my_str_list": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "'my_str_list' must match schema",
        },
        "my_int_list": {
            "bsonType": "array",
            "items": {"bsonType": "int"},
            "description": "'my_int_list' must match schema",
        },
        "my_float_list": {
            "bsonType": "array",
            "items": {"bsonType": "double"},
            "description": "'my_float_list' must match schema",
        },
        "my_optional_list": {
            "oneOf": [
                {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                },
                {"bsonType": "null"},
            ],
            "description": "'my_optional_list' must match schema",
        },
        "my_int_or_bool_list": {
            "bsonType": "array",
            "items": {"oneOf": [{"bsonType": "int"}, {"bsonType": "bool"}]},
            "description": "'my_int_or_bool_list' must match schema",
        },
    },
}


def test_basic_bson_list_generation():
    # Given: A class with different types of lists including optional and union types
    validation_title = "Test"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            **expected_mock_class_bson_schema,
        }
    }

    # When: Generating BSON validation rules from the class
    actual_schema = MockClass.generate_validation_rules(validation_title)

    # Then: The schema should match the expected structure
    assert actual_schema == expected_schema


def test_nested_bson_list_generation():
    # Given: A class containing a list of another MongoValidator-based class
    validation_title = "Test Nested"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["my_mock_class_list"],
            "properties": {
                "my_mock_class_list": {
                    "bsonType": "array",
                    "items": expected_mock_class_bson_schema,
                    "description": "'my_mock_class_list' must match schema",
                }
            },
        }
    }

    # When: Generating BSON validation rules from the nested class
    actual_schema = MyMockListClass.generate_validation_rules(validation_title)

    # Then: The result should match the nested list schema
    assert actual_schema == expected_schema


def test_list_without_type_bson_generation():
    # Given: A class with a generic untyped list
    validation_title = "Untyped List"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["generic_list"],
            "properties": {
                "generic_list": {
                    "bsonType": "array",
                    "description": "'generic_list' must match schema",
                }
            },
        }
    }

    # When: Generating BSON validation rules
    actual_schema = ListWithoutType.generate_validation_rules(validation_title)

    # Then: The generated schema should reflect an untyped list
    assert actual_schema == expected_schema


def test_list_with_len_bson_generation():
    # Given: A class with a list annotated with length constraints
    validation_title = "List With Len"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["fixed_list"],
            "properties": {
                "fixed_list": {
                    "bsonType": "array",
                    "items": {"bsonType": "int"},
                    "minItems": 2,
                    "maxItems": 5,
                    "description": "'fixed_list' must match schema",
                }
            },
        }
    }

    # When: Generating BSON validation schema
    actual_schema = ListWithLen.generate_validation_rules(validation_title)

    # Then: The schema should reflect the length constraints
    assert actual_schema == expected_schema


def test_list_with_literal_bson_generation():
    # Given: A class with a list of Literal values
    validation_title = "List With Literal"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["state_list"],
            "properties": {
                "state_list": {
                    "bsonType": "array",
                    "items": {"enum": ["on", "off"], "bsonType": "string"},
                    "description": "'state_list' must match schema",
                }
            },
        }
    }

    # When: Generating validation schema for literal values
    actual_schema = ListWithLiteral.generate_validation_rules(validation_title)

    # Then: The schema must match the expected enum representation
    assert actual_schema == expected_schema


def test_nested_list_bson_generation():
    # Given: A class with a list of lists (matrix structure)
    validation_title = "Nested List"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["matrix"],
            "properties": {
                "matrix": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "array",
                        "items": {"bsonType": "int"},
                    },
                    "description": "'matrix' must match schema",
                }
            },
        }
    }

    # When: Generating validation rules for nested lists
    actual_schema = NestedList.generate_validation_rules(validation_title)

    # Then: The generated schema must reflect the matrix structure
    assert actual_schema == expected_schema


def test_optional_list_of_model_bson_generation():
    # Given: A class with an optional list of embedded models
    class Child(MongoValidator):
        field: int

    class Parent(MongoValidator):
        children: Optional[List[Child]]

    validation_title = "Optional List of Model"
    expected_schema: dict[str, Any] = {
        "$jsonSchema": {
            "title": f"{validation_title} Validation",
            "bsonType": "object",
            "required": ["children"],
            "properties": {
                "children": {
                    "oneOf": [
                        {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["field"],
                                "properties": {
                                    "field": {
                                        "bsonType": "int",
                                        "description": "'field' must match schema",
                                    }
                                },
                            },
                        },
                        {"bsonType": "null"},
                    ],
                    "description": "'children' must match schema",
                }
            },
        }
    }

    # When: Generating schema for optional embedded models
    actual_schema = Parent.generate_validation_rules(validation_title)

    # Then: The schema must correctly handle optional list of nested models
    assert actual_schema == expected_schema
