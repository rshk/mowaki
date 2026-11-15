"""
Configuration of Authentication flows and machinery.
"""

from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.repo import AuthnFlowRepo
from app.lib.flows.registry import FlowRegistry
from app.lib.flows.types import FlowKind

flow_registry = FlowRegistry()
flow_registry[FlowKind("login")] = LoginFlowFactory()

flow_repo = AuthnFlowRepo(flow_registry)
