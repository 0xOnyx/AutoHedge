"""
Trading module - Orchestrates the trading cycle and state machine.
Implements the Processing layer of the Data Flow diagram.

Data Flow - Processing:
Technical/Fundamental -> Quant Analysis -> Risk Analysis -> Order Generation
"""
from autohedge.trading.state_machine import TradingStateMachine
from autohedge.trading.cycle import TradingCycle
from autohedge.trading.tasks import TaskFactory

__all__ = [
    "TradingStateMachine",
    "TradingCycle",
    "TaskFactory",
]

