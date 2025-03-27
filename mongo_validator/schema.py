from types import UnionType
from typing import Annotated, Any, Callable, List, Literal, Union, get_args, get_origin
from annotated_types import Len

from mongo_validator.bson_type import BSONType, get_bson_type_for
from mongo_validator.custom_types import Long

BSONSchemaCallback = Callable[[Any], dict[str, Any] | None]


def unwrap_annotated(type_hint: Any) -> tuple[Any, tuple[Any, ...]]:
    """
    Unwraps a type annotated with `typing.Annotated` to extract its base type and metadata annotations.

    This function is used to separate the underlying type from its annotations when using
    `Annotated[...]`, which allows attaching metadata (e.g., validation rules) to type hints.

    Args:
        type_hint (Any): A Python type hint that may or may not be an instance of `Annotated`.

    Returns:
        tuple:
            - The unwrapped base type (e.g., `int` from `Annotated[int, ...]`).
            - A tuple of annotations (empty if not `Annotated`).
    """
    if get_origin(type_hint) is Annotated:
        base, *annotations = get_args(type_hint)
        return base, tuple(annotations)

    return type_hint, ()


def build_bson_schema(
    type_hint: Any,
    get_bson_schema_for: BSONSchemaCallback,
) -> dict[str, Any]:
    """
    Builds a BSON schema representation for a given Python type annotation, including support
    for Annotated metadata, Literal types, Lists, Unions, and custom BSON mappings.

    This function recursively generates a MongoDB-compatible BSON schema based on a type hint,
    with extended support for custom annotations and type handling logic.

    Args:
        type_hint (Any): The Python type annotation to convert (e.g., str, int, list[str], Union[int, str], etc.).
        get_bson_scheme_for (Callable[[Any], dict[str, Any] | None]):
            A callback that returns a full BSON schema dict for a given type if it's a recognized custom schema.
            Returns None if the type should be processed using default logic.

    Returns:
        Dict (dict[str, Any]): A dictionary representing the BSON schema corresponding to the provided type.

    Raises:
        ValueError: If the type cannot be mapped to a BSON schema using the provided or default logic.

    Behavior:
        - If the type is `Annotated`, it unwraps the base type and retains associated metadata (e.g., constraints).
        - If the type is a `Union`, it delegates to `build_bson_schema_for_union` and may return a `oneOf` schema.
        - If the type is a `List`, it delegates to `build_bson_schema_for_list`, which also handles
          optional constraints (e.g., `Len`) from annotations.
        - If the type is a `Literal`, it uses `build_bson_schema_for_literal` to define an enum-like schema.
        - If the `get_bson_schema_for` callback provides a custom schema for the type, it is returned directly.
        - If a `Long` annotation is found, it returns the BSON type `"long"` regardless of the underlying type.
        - If the type matches a known BSON type (via `get_bson_type_for`), it returns a basic BSON type schema.
        - If none of the above apply, a `ValueError` is raised.
    """
    type_hint, annotations = unwrap_annotated(type_hint)
    origin = get_origin(type_hint)

    if origin in (Union, UnionType):
        return build_bson_schema_for_union(type_hint, get_bson_schema_for)

    if origin in (list, List):
        return build_bson_schema_for_list(type_hint, annotations, get_bson_schema_for)

    if origin is Literal:
        return build_bson_schema_for_literal(type_hint)

    bson_scheme = get_bson_schema_for(type_hint)

    if bson_scheme is not None:
        return bson_scheme

    for ann in annotations:
        if ann is Long:
            return {"bsonType": BSONType.LONG.value}

    bson_type = get_bson_type_for(type_hint)

    if bson_type:
        return {"bsonType": bson_type}

    raise ValueError(f"Property type not supported: {type_hint}")


def build_bson_schema_for_union(
    type_hint: Any,
    get_bson_schema_for: BSONSchemaCallback,
) -> dict[str, Any]:
    """
    Builds a BSON schema for a Union type.

    This function handles Python `Union` or `UnionType` annotations by generating
    a BSON schema that allows multiple possible types for a single field.

    Args:
        type_hint (Any): A Python `Union` type annotation (e.g., Union[str, int]).
        get_bson_schema_for (BSONSchemaCallback): A callback used to resolve custom
            schemas for each type within the union.

    Returns:
        Dict (dict[str, Any]): A BSON schema dictionary. If the union contains only one
            type, returns that type's schema directly. Otherwise, returns a schema
            using "oneOf" with all possible type schemas.

    Behavior:
        - Recursively applies `build_bson_schema` to each type in the union.
        - If there's only one option, unwraps it (avoids unnecessary "oneOf").
        - Otherwise, wraps all options under "oneOf" to represent multiple allowed types.
    """
    args = get_args(type_hint)
    options = [build_bson_schema(t, get_bson_schema_for) for t in args]
    return next(iter(options)) if len(options) == 1 else {"oneOf": options}


def build_bson_schema_for_list(
    type_hint: Any,
    annotations: tuple[Any, ...],
    get_bson_schema_for: BSONSchemaCallback,
) -> dict[str, Any]:
    """
    Builds a BSON schema for a list type, including optional metadata constraints
    extracted from annotations (e.g., min/max item count).

    This function handles the specific case where the input type is a list or similar
    collection, and allows metadata (such as a length constraint) to be applied via
    annotations like `Annotated[..., Len(...)]`.

    Args:
        type_hint (Any): The list type to be converted (e.g., list[str], List[int], etc.).
        annotations (tuple[Any, ...]): A tuple of metadata annotations, typically unwrapped
            from an `Annotated` type using `unwrap_annotated`.
        get_bson_schema_for (Callable[[Any], dict[str, Any] | None]): A callback used to resolve custom schemas
            for types nested within the list.

    Returns:
        Dict (dict[str, Any]): A BSON schema dictionary for the list type, with optional minItems
        and maxItems if a `Len` annotation is present.

    Behavior:
        - Recursively applies `build_bson_schema` to the list's item type.
        - If a `Len` annotation is found, applies `minItems` and `maxItems` constraints
          to the schema.
        - Returns a BSON schema with `bsonType: "array"` and an `items` definition.
    """
    inner_type = get_args(type_hint)[0] if get_args(type_hint) else Any

    schema: dict[str, Any] = {
        "bsonType": BSONType.ARRAY.value,
        "items": build_bson_schema(inner_type, get_bson_schema_for),
    }

    for ann in annotations:
        if not isinstance(ann, Len):
            continue

        schema["minItems"] = ann.min_length

        if ann.max_length is not None:
            schema["maxItems"] = ann.max_length

    return schema


def build_bson_schema_for_literal(type_hint: Any) -> dict[str, Any]:
    """
    Builds a BSON schema for a Literal type.

    This function generates a schema that restricts the value of a field to a fixed
    set of allowed values, as defined by the `Literal[...]` type from the `typing` module.

    Args:
        type_hint (Any): A Python `Literal` type annotation (e.g., Literal["a", "b"], Literal[1, 2, 3]).

    Returns:
        Dict (dict[str, Any]): A BSON schema dictionary with an "enum" key listing the allowed values.
            If all literals are of the same type and it maps to a BSON type,
            the corresponding "bsonType" is included.

    Behavior:
        - Extracts all allowed literal values and places them under the "enum" key.
        - If all literals are of the same base type and it maps to a BSON type
          (e.g., all strings or all integers), it adds a "bsonType" key.
    """
    args = get_args(type_hint)
    types: list[type[Any]] = [type(arg) for arg in args]

    literal_types: set[type[Any]] = set(types)
    schema: dict[str, Any] = {"enum": list(args)}

    if len(literal_types) == 1:
        bson_type = get_bson_type_for(next(iter(literal_types)))
        if bson_type:
            schema["bsonType"] = bson_type

    return schema
