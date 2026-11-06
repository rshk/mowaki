"""
Configuration of Authentication flows and machinery.
"""

from app.core.authn.flows.repo import AuthnFlowRepo
from app.lib.flows.registry import FlowRegistry

flow_registry = FlowRegistry()

# TODO: add flows to the registry

flow_repo = AuthnFlowRepo(flow_registry)
