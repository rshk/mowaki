from typing import Any, Self

import pydantic


class BaseModel(pydantic.BaseModel):
    """Custom based for models"""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)
