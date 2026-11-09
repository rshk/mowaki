from typing import NewType

from app.lib.types import JSONObject

FlowKind = NewType("FlowKind", str)
FlowParams = NewType("FlowParams", JSONObject)
FlowState = NewType("FlowState", JSONObject)
FlowAction = NewType("FlowAction", JSONObject)
FlowChallenge = NewType("FlowChallenge", JSONObject)
