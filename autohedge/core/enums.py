"""
Enumerations for the trading system.
Defines states and decisions used throughout the trading cycle.
"""
from enum import Enum


class TradingState(str, Enum):
    """
    Trading cycle states following the state machine diagram.
    
    State Machine Flow:
    [*] --> INITIALIZATION
    INITIALIZATION --> THESIS_GENERATION
    THESIS_GENERATION --> QUANT_ANALYSIS
    QUANT_ANALYSIS --> RISK_ASSESSMENT
    RISK_ASSESSMENT --> ORDER_GENERATION (if approved)
    RISK_ASSESSMENT --> THESIS_GENERATION (if rejected)
    ORDER_GENERATION --> ORDER_EXECUTION
    ORDER_EXECUTION --> MONITORING
    MONITORING --> COMPLETE
    """
    INITIALIZATION = "initialization"
    THESIS_GENERATION = "thesis_generation"
    QUANT_ANALYSIS = "quant_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    ORDER_GENERATION = "order_generation"
    ORDER_EXECUTION = "order_execution"
    MONITORING = "monitoring"
    COMPLETE = "complete"


class RiskDecision(str, Enum):
    """
    Risk assessment decision outcomes.
    Determines whether the trading cycle proceeds or retries.
    """
    APPROVED = "approved"
    REJECTED = "rejected"


