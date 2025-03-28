## 1.0.0

Initial stable release of `mongo_validations_generator`.

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
