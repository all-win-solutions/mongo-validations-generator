# mongo_validator

**mongo_validator** is a lightweight Python library for generating MongoDB JSON Schema validation rules using standard Python type annotations and Pydantic models.

It allows you to define your MongoDB collection schemas declaratively with Python classes, while supporting advanced typing features like `Annotated`, `Literal`, `Union`, custom validation markers, and nested models.

---

## Features

- ✅ Auto-generates `$jsonSchema` validation for MongoDB
- ✅ Support for Python type hints: `str`, `int`, `float`, `bool`, `list`, `None`
- ✅ Nested objects using Pydantic-style inheritance
- ✅ Annotated constraints using `Annotated[..., Len(...)]`
- ✅ Support for `Union`, `Optional`, and `Literal` types
- ✅ Custom BSON type markers (e.g., `Long`)
- ✅ Ability to ignore fields with `SchemaIgnored`

---

## 🚀 Getting Started

### 1. Define a model

```python
from annotated_types import Len
from mongo_validator import MongoValidator, Long, SchemaIgnored
from typing import Annotated, Literal

class Product(MongoValidator):
    name: str
    description: str
    categories: list[str]
    price: Annotated[int, Long]
    tags: Annotated[list[str], Len(1)]
    internal_code: Annotated[str, SchemaIgnored]
    status: Literal["active", "archived"]
```

### 2. Generate the schema

```python
import json

print(json.dumps(Product.validation_rules("Product"), indent=2))
```

#### output:
```json
{
  "$jsonSchema": {
    "title": "Product Validation",
    "bsonType": "object",
    "required": [
      "name",
      "description",
      "categories",
      "price",
      "tags",
      "status"
    ],
    "properties": {
      "name": {
        "bsonType": "string",
        "description": "'name' must match schema"
      },
      "description": {
        "bsonType": "string",
        "description": "'description' must match schema"
      },
      "categories": {
        "bsonType": "array",
        "items": {
          "bsonType": "string"
        },
        "description": "'categories' must match schema"
      },
      "price": {
        "bsonType": "long",
        "description": "'price' must match schema"
      },
      "tags": {
        "bsonType": "array",
        "items": {
          "bsonType": "string"
        },
        "minItems": 1,
        "description": "'tags' must match schema"
      },
      "status": {
        "enum": ["active", "archived"],
        "bsonType": "string",
        "description": "'status' must match schema"
      }
    }
  }
}

```
