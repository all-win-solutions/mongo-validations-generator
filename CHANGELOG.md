## 1.1.0

- Support for `BSONDecimal128` as a custom scalar type:
  - Accepts `str`, `Decimal`, or `Decimal128`
  - Converts input to MongoDB's `Decimal128` format
  - Serializes to `str` in `model_dump()` (e.g., `"123.45"`)
  - Integrated into schema generation with `bsonType: "decimal"`
- New type mapping in `TYPE_MAP`: `BSONDecimal128 -> "decimal"`
- **Added `pymongo` as a required dependency** to enable support for `Decimal128`

## 1.0.0

Initial stable release of `mongo-validations-generator`.

### Features

- ✅ **BSON Schema Generation** from Pydantic-style classes using standard Python type annotations.
- ✅ Support for core BSON types:
  - `str` → `"string"`
  - `int` → `"int"`
  - `float` → `"double"`
  - `bool` → `"bool"`
  - `list[...]` → `"array"`
  - `None` / `Optional[...]` → `"null"`
  - `Literal[...]` → `"enum"`
  - `MongoValidator` subclasses → `"object"`
  - `Annotated[int, Long]` → `"long"`
- ✅ Nested object support via model composition.
- ✅ `Union` and `Optional` support using `oneOf` resolution.
- ✅ Array validation with constraints using `Annotated[list[T], Len(...)]`.
- ✅ Field-level schema descriptions auto-generated.
- ✅ Custom types:
  - `Long` for `bsonType: "long"`
  - `SchemaIgnored` to exclude fields from validation
- ✅ Flexible schema generator: supports dynamic model inspection without requiring instantiated objects.
