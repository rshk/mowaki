"""
Utilities for documenting flows.
"""

from dataclasses import dataclass

import pydantic

from app.lib.types import JSONObject

from .types import FlowKind

ParamsType = pydantic.BaseModel
StateType = pydantic.BaseModel
ActionType = pydantic.BaseModel


class FlowObjectDocsRegistry:
    _flow_docs: dict[FlowKind, FlowDocs]
    _state_docs: dict[type[StateType], StateDocs]

    def __init__(self):
        self._flow_docs = {}
        self._state_docs = {}

    def document_flow(
        self,
        kind: FlowKind,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        params: type[ParamsType] | None = None,
        states: list[StateRel] | None = None,
    ) -> FlowDocs:
        """
        Add documentation for a Flow.

        Args:
            kind:
                The FlowKind we're documenting.
            title:
                A short title for the flow.
            summary:
                A one-line description of the flow.
            description:
                A longer description of the flow.
            params:
                A Pydantic model used to load flow parameters, if any.
            states:
                A list of initial states for the flow.
        """

        if title is None:
            title = str(kind)

        docs = FlowDocs(
            title=title,
            summary=summary,
            description=description,
            params_schema=params.model_json_schema() if params is not None else None,
            states=states,
        )
        self._flow_docs[kind] = docs
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
        """
        Add documentation for a flow state.

        Args:
            obj:
                Type of a state block to be documented. Will be used
                to provide default values for some of the other
                fields.
            kind:
                Value of the state "kind". Retrieved from the model if
                set to None.
            title:
                A short title for the flow state.
            summary:
                A one-line description of the flow state.
            description:
                A longer description of the flow state.
            actions:
                A list of actions that may be performed in this state.
        """
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

    def generate_flow_docs(self, kind: FlowKind):
        """
        Generate full documentation for a flow, as a JSON object.
        """

        states: dict[str, StateDocs] = {}
        states_docs_json: dict[str, JSONObject] = {}

        def generate_flow_docs(kind: FlowKind) -> JSONObject:
            obj = self._flow_docs[kind]
            return {
                "title": obj.title,
                "summary": obj.summary,
                "description": obj.description,
                "params_schema": obj.params_schema,
                "states": [generate_state_rel_docs(x) for x in obj.states],
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

        flow_docs_json = generate_flow_docs(kind)
        return {
            "flow": flow_docs_json,
            "states": states_docs_json,
        }

    def _get_or_create_state_docs(self, obj: type[StateType]) -> StateDocs:
        if obj not in self._state_docs:
            self.document_state(obj)
        docs = self._state_docs[obj]
        assert isinstance(docs, StateDocs)
        return docs


class FlowDocs:
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


class StateDocs:
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


class ActionDocs:
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
