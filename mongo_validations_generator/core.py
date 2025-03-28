from typing import Any, get_type_hints
from pydantic import BaseModel
from mongo_validations_generator.schema import build_bson_schema, unwrap_annotated
from mongo_validations_generator.custom_types import SchemaIgnored

Dict = dict[str, Any]


class MongoValidator(BaseModel):
    @classmethod
    def generate_validation_rules(cls, title: str) -> Dict:
        """
        Generates a MongoDB JSON schema validation rule for the class.

        This method builds a JSON schema document that can be used to enforce
        data validation rules on a MongoDB collection based on the class's annotated fields.

        Args:
            title (str): A descriptive title for the schema, used in the 'title' field of the JSON schema.

        Returns:
            Dict (dict[str, Any]): A dictionary representing the MongoDB JSON schema validation rule,
                including required fields and BSON type mappings based on class annotations.

        Example:
        ```
        {
            "$jsonSchema": {
                "title": "User Validation",
                "bsonType": "object",
                "required": ["name", "age"],
                "properties": {
                    "name": {
                        "bsonType": "string",
                        "description": "'name' must match schema"
                    },
                    "age": {
                        "bsonType": "int",
                        "description": "'age' must match schema"
                    }
                }
            }
        }
        ```
        """
        return {
            "$jsonSchema": {
                "title": f"{title} Validation",
                **cls.parse_object(),
            }
        }

    @classmethod
    def parse_object(cls) -> Dict:
        """
        Parses the class's annotated fields into a BSON object schema.

        This method inspects the class-level type annotations using `get_type_hints` with
        `include_extras=True` to preserve `Annotated` metadata. It generates a MongoDB-compatible
        BSON schema describing the object structure, including required fields and property schemas.

        Returns:
            Dict (dict[str, Any]): A dictionary representing a BSON object schema, with keys:
                - "bsonType": Always set to "object".
                - "required": A list of all annotated field names.
                - "properties": A dictionary mapping field names to their respective BSON schemas.

        Behavior:
            - Uses `get_type_hints(..., include_extras=True)` to capture `Annotated` metadata.
            - Ignores any field annotated with `Annotated[..., SchemaIgnored]`.
            - Assumes all annotated fields are required.
        """
        type_hints = get_type_hints(cls, include_extras=True)
        parsed_properties: dict[str, dict[str, Any]] = {}
        required_fields: list[str] = []

        for name, type_hint in type_hints.items():
            property_schema = cls.__parse_property(name, type_hint)

            if property_schema is None:
                continue

            parsed_properties[name] = property_schema
            required_fields.append(name)

        return {
            "bsonType": "object",
            "required": required_fields,
            "properties": parsed_properties,
        }

    @staticmethod
    def __parse_property(name: str, type_hint: Any) -> Dict | None:
        _, annotations = unwrap_annotated(type_hint)

        for ann in annotations:
            if ann is SchemaIgnored:
                return None

        schema = build_bson_schema(type_hint, MongoValidator.get_bson_schema_for)

        return {
            **schema,
            "description": f"'{name}' must match schema",
        }

    @staticmethod
    def get_bson_schema_for(type_hint: Any) -> dict[str, Any] | None:
        """
        Get the BSON schema for a given type if it's a MongoValidator subclass.

        This function checks if the input type is a subclass of MongoValidator
        and returns its parsed object representation if it is.

        Args:
            type_hint (Any): The type to check for BSON schema.

        Returns:
            Dict (dict[str, Any] | None): The parsed object representation of the BSON schema
                if the input is a MongoValidator subclass,
                or None if it's not.
        """
        if isinstance(type_hint, type) and issubclass(type_hint, MongoValidator):
            return type_hint.parse_object()

        return None
