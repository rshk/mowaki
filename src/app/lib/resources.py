from typing import Any

RESOURCE_DEFAULT_NAME = "default"


class ResourceID:
    """Base class for resource IDs"""

    __slots__ = ["name"]

    name: str

    def __init__(self, name=RESOURCE_DEFAULT_NAME):
        self.name = name

    def __hash__(self):
        return hash((type(self), self.name))


class ResourcesRegistry:
    __slots__ = ["resources"]

    resources: dict[ResourceID, Any]

    def __init__(self):
        self.resources = {}

    def add(self, key: ResourceID, resource: Any) -> None:
        self.resources[key] = resource

    def get(self, key: ResourceID) -> Any | None:
        return self.resources.get(key)

    def require(self, key: ResourceID) -> Any:
        return self.resources[key]

    def delete(self, key: ResourceID) -> None:
        self.resources.pop(key, None)

    def clone(self):
        new = type(self)()
        new.resources = {**self.resources}
        return new
