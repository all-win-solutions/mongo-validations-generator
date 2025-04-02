from decimal import Decimal
from typing import Any
from bson import Decimal128
from pydantic import ValidationError
import pytest

from mongo_validations_generator import MongoValidator, BSONDecimal128


class PriceModel(MongoValidator):
    price: BSONDecimal128


@pytest.mark.parametrize(
    "input_value,expected_decimal",
    [
        ("123.45", Decimal("123.45")),
        (Decimal("77.01"), Decimal("77.01")),
        (Decimal128("42.0"), Decimal("42.0")),
    ],
)
def test_bson_decimal_model_accepts_valid_values(
    input_value: Any,
    expected_decimal: Decimal,
):
    # Given: A valid value (string, Decimal, or Decimal128) representing a decimal
    # When: Creating the model with this value
    model = PriceModel(price=input_value)
    actual_decimal = model.price.to_decimal()

    # Then: The field must be stored as a Decimal128 and convert to the expected Decimal
    assert isinstance(model.price, Decimal128)
    assert actual_decimal == expected_decimal


@pytest.mark.parametrize(
    "invalid_input",
    [
        "not_a_number",
        {},
        [],
        True,
        object(),
        10,
        10.0,
    ],
)
def test_bson_decimal_model_rejects_invalid_values(invalid_input: Any):
    # Given: An invalid input that cannot be converted to BSONDecimal128

    # When / Then: Model instantiation must raise a ValidationError
    with pytest.raises(ValidationError):
        PriceModel(price=invalid_input)


def test_bson_decimal_serialization_to_decimal():
    # Given: A model with a decimal price as a string
    model = PriceModel(price="100.50")  # type: ignore

    # When: Dumping the model to a dictionary
    data = model.model_dump()

    # Then: The serialized value must be a Decimal128
    assert data == {"price": Decimal128("100.50")}


def test_bson_decimal_str_and_repr():
    # Given: A BSONDecimal128 instance created from a string
    instance = BSONDecimal128("19.99")

    # When: Calling str(), repr() and to_decimal()
    # Then: Outputs should be human-readable and preserve decimal precision
    assert str(instance) == "19.99"
    assert "BSONDecimal128" in repr(instance)
    assert instance.to_decimal() == Decimal("19.99")


def test_model_validate_supports_decimal_inputs():
    # Given: A raw input dictionary with a decimal value as a string
    raw_input = {"price": "15.75"}

    # When: Validating the input using Pydantic's model_validate
    model = PriceModel.model_validate(raw_input)

    # Then: The model should be correctly instantiated with a Decimal128 value
    assert isinstance(model, PriceModel)
    assert isinstance(model.price, Decimal128)
    assert model.price.to_decimal() == Decimal("15.75")
