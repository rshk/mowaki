"""
Utilities for documenting flows.
"""

# FIXME: Action only makes sense in the context of a *state*, so we
# should probably move most of its documentation from ActionDocs to
# ActionRel. State documentation is fine as it is.

from dataclasses import dataclass

import pydantic

from app.lib.types import JSONObject

from .factory import FlowFactory

FactoryType = FlowFactory
ParamsType = pydantic.BaseModel
StateType = pydantic.BaseModel
ActionType = pydantic.BaseModel


class FlowObjectDocsRegistry:
    _flow_docs: dict[type[FactoryType], FactoryDocs]
    _state_docs: dict[type[StateType], StateDocs]

    def __init__(self):
        self._flow_docs = {}
        self._state_docs = {}

    def document_flow(
        self,
        obj: type[FactoryType],
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        params: type[ParamsType] | None = None,
        states: list[StateRel] | None = None,
    ) -> FactoryDocs:
        if title is None:
            title = _extract_object_title(obj)
        if description is None:
            description = _extract_object_description(obj)

        docs = FactoryDocs(
            title=title,
            summary=summary,
            description=description,
            params_schema=params.model_json_schema() if params is not None else None,
            states=states,
        )
        self._flow_docs[obj] = docs
        return docs

    def document_state(
        self,
        obj: type[StateType],
        kind: str | None = None,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        actions: list[ActionDocs] | None = None,
    ) -> StateDocs:
        docs = StateDocs(
            state=obj,
            kind=kind,
            title=title,
            summary=summary,
            description=description,
            schema=obj.model_json_schema(),
            actions=actions,
        )
        self._state_docs[obj] = docs
        return docs

    def generate_flow_docs(self, factory: type[FlowFactory]):
        """Generate full documentation for a flow"""

        states: dict[str, StateDocs] = {}
        states_docs_json: dict[str, JSONObject] = {}

        def generate_factory_docs(factory: type[FlowFactory]) -> JSONObject:
            factory_docs = self._get_or_create_factory_docs(factory)
            assert isinstance(factory_docs, FactoryDocs)

            return {
                "title": factory_docs.title,
                "summary": factory_docs.summary,
                "description": factory_docs.description,
                "params_schema": factory_docs.params_schema,
                "states": [generate_state_rel_docs(x) for x in factory_docs.states],
            }

        def generate_state_rel_docs(state_rel: StateRel) -> JSONObject:
            return {
                "description": state_rel.description,
                "state_kind": get_state_kind(state_rel.state),
            }

        def get_state_kind(obj: type[StateType]) -> str:
            docs = self._get_or_create_state_docs(obj)
            assert isinstance(docs, StateDocs)

            if docs.kind in states:
                if states[docs.kind] is not docs:
                    raise TypeError(f"Multiple states found for kind: {docs.kind}")
                return docs.kind

            states[docs.kind] = docs
            states_docs_json[docs.kind] = generate_state_docs(docs)
            return docs.kind

        def generate_state_docs(obj: StateDocs) -> JSONObject:
            return {
                "kind": obj.kind,
                "title": obj.title,
                "summary": obj.summary,
                "description": obj.description,
                # TODO: add "challenge" schema here?
                "actions": [generate_action_docs(x) for x in obj.actions],
            }

        def generate_action_docs(obj: ActionDocs) -> JSONObject:
            return {
                "kind": obj.kind,
                "title": obj.title,
                "summary": obj.summary,
                "description": obj.description,
                "schema": obj.schema,
                "next_states": [generate_state_rel_docs(x) for x in obj.next_states],
            }

        factory_docs_json = generate_factory_docs(factory)
        return {
            "flow": factory_docs_json,
            "states": states_docs_json,
        }

    def _get_or_create_factory_docs(self, obj: type[FactoryType]) -> FactoryDocs:
        if obj not in self._flow_docs:
            self.document_flow(obj)
        docs = self._flow_docs[obj]
        assert isinstance(docs, FactoryDocs)
        return docs

    def _get_or_create_state_docs(self, obj: type[StateType]) -> StateDocs:
        if obj not in self._state_docs:
            self.document_state(obj)
        docs = self._state_docs[obj]
        assert isinstance(docs, StateDocs)
        return docs


class ObjectDocs:
    pass


class FactoryDocs(ObjectDocs):
    title: str | None
    summary: str | None
    description: str | None
    params_schema: JSONObject | None
    states: list[StateRel]

    def __init__(
        self,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        params_schema: JSONObject | None = None,
        states: list[StateRel] | None = None,
    ):
        self.title = title
        self.summary = summary
        self.description = description
        self.params_schema = params_schema
        self.states = states if states is not None else []


class StateDocs(ObjectDocs):
    kind: str
    title: str | None
    summary: str | None
    description: str | None
    schema: JSONObject | None
    actions: list[ActionDocs]

    def __init__(
        self,
        state: type[StateType] | None = None,
        *,
        kind: str | None = None,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        schema: JSONObject | None = None,
        actions: list[ActionDocs] | None = None,
    ):
        if state is not None:
            if kind is None:
                kind = _extract_object_kind(state)
            if title is None:
                title = _extract_object_title(state)
            if description is None:
                description = _extract_object_description(state)

        if kind is None:
            raise ValueError(
                "State kind must be specified, either explicitly or in the action type"
            )

        self.kind = kind
        self.title = title
        self.summary = summary
        self.description = description
        self.schema = schema
        self.actions = actions if actions is not None else []


class ActionDocs(ObjectDocs):
    kind: str
    title: str | None
    summary: str | None
    description: str | None
    schema: JSONObject | None
    next_states: list[StateRel]

    def __init__(
        self,
        action: type[ActionType] | None = None,
        *,
        kind: str | None = None,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        schema: JSONObject | None = None,
        states: list[StateRel] | None = None,
    ):

        if action is not None:
            if kind is None:
                kind = _extract_object_kind(action)
            if title is None:
                title = _extract_object_title(action)
            if description is None:
                description = _extract_object_description(action)
            if schema is None:
                schema = action.model_json_schema()

        if kind is None:
            raise ValueError(
                "Action kind must be specified, either explicitly or in the action type"
            )

        self.kind = kind
        self.title = title
        self.summary = summary
        self.description = description
        self.schema = schema
        self.next_states = states if states is not None else []


@dataclass
class StateRel:
    state: type[StateType]
    title: str | None = None
    description: str | None = None


def _extract_object_kind(obj: type) -> str:
    if issubclass(obj, pydantic.BaseModel):
        try:
            return obj.model_fields["kind"].default
        except KeyError:
            pass

    return obj.__name__  # fallback


def _extract_object_title(obj: type) -> str | None:
    return obj.__name__


def _extract_object_description(obj: type) -> str | None:
    return obj.__doc__
