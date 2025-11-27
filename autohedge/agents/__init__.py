"""
Agents module - Contains AI agent definitions and configurations.
Each agent has a specific role in the trading cycle following the sequence diagram.

Sequence Diagram:
Client -> Director -> Quant -> Risk -> Execution -> Director -> Client
"""
from autohedge.agents.factory import AgentFactory
from autohedge.agents.prompts import (
    DIRECTOR_PROMPT,
    QUANT_PROMPT,
    RISK_PROMPT,
    EXECUTION_PROMPT,
)

__all__ = [
    "AgentFactory",
    "DIRECTOR_PROMPT",
    "QUANT_PROMPT",
    "RISK_PROMPT",
    "EXECUTION_PROMPT",
]

