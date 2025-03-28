import re
from typing import Union
import pytest
from mongo_validations_generator import MongoValidator


class InvalidModel(MongoValidator):
    config: dict  # type: ignore


class InvalidSetModel(MongoValidator):
    tags: set[str]


class InvalidUnion(MongoValidator):
    field: Union[str, dict]  # type: ignore


class InvalidUntyped(MongoValidator):
    data: list[object]


class InvalidTuple(MongoValidator):
    position: tuple[int, int]


def test_fails_on_dict_field():
    # Given: A model with a field of unsupported type dict
    property_type = dict

    # When / Then: Generating validation rules should raise a ValueError
    with pytest.raises(
        ValueError,
        match=re.escape(f"Property type not supported: {property_type}"),
    ):
        InvalidModel.generate_validation_rules("DictField")


def test_fails_on_set_field():
    # Given: A model with a field of unsupported type set[str]
    property_type = set[str]

    # When / Then: Attempting to generate rules should raise a ValueError
    with pytest.raises(
        ValueError,
        match=re.escape(f"Property type not supported: {property_type}"),
    ):
        InvalidSetModel.generate_validation_rules("SetField")


def test_fails_on_union_with_unsupported_type():
    # Given: A model with a Union including an unsupported type dict
    property_type = dict  # type: ignore

    # When / Then: Validation rule generation must fail with ValueError
    with pytest.raises(
        ValueError,
        match=re.escape(f"Property type not supported: {property_type}"),
    ):
        InvalidUnion.generate_validation_rules("UnionDictField")


def test_fails_on_untyped_list_with_unsupported_element():
    # Given: A model with a list containing elements of type object (unsupported)
    property_type = object

    # When / Then: Rule generation should raise a ValueError
    with pytest.raises(
        ValueError,
        match=re.escape(f"Property type not supported: {property_type}"),
    ):
        InvalidUntyped.generate_validation_rules("UntypedList")


def test_fails_on_tuple_field():
    # Given: A model with a tuple field, which is not supported
    property_type = tuple[int, int]

    # When / Then: Generation must raise a ValueError due to unsupported type
    with pytest.raises(
        ValueError,
        match=re.escape(f"Property type not supported: {property_type}"),
    ):
        InvalidTuple.generate_validation_rules("TupleField")


def test_fails_on_missing_annotation():
    # Given: A class with a field declared without a type annotation

    # When / Then: Instantiating the class should raise a TypeError
    with pytest.raises(TypeError) as excinfo:

        class BadModel(MongoValidator):  # type: ignore
            field = "value"

    # Then: Error message must indicate missing annotation
    assert "non-annotated attribute" in str(excinfo.value)
