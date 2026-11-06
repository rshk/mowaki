from collections.abc import Iterator, MutableMapping

from app.types.auth.auth_flow import FlowKind

from .factory import FlowFactory


class FlowRegistry(MutableMapping):
    _flows: dict[FlowKind, FlowFactory]

    def __init__(self):
        self._flows = {}

    def __getitem__(self, key, /) -> FlowFactory:
        return self._flows[key]

    def __setitem__(self, key: FlowKind, value: FlowFactory, /) -> None:
        if key in self._flows:
            raise KeyError(f"Duplicate key: {key}")
        self._flows[key] = value

    def __delitem__(self, key: FlowKind, /) -> None:
        del self._flows[key]

    def __iter__(self) -> Iterator[FlowKind]:
        return iter(self._flows)

    def __len__(self) -> int:
        return len(self._flows)
