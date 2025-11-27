"""
Trading state machine module.
Manages state transitions during the trading cycle.

State Machine Diagram:
┌─────────────────┐
│  [*] Initial    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Initialization  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ThesisGeneration │◄─────────┐
└────────┬────────┘          │
         │                   │
         ▼                   │
┌─────────────────┐          │
│  QuantAnalysis  │          │
└────────┬────────┘          │
         │                   │
         ▼                   │
┌─────────────────┐          │
│ RiskAssessment  │──────────┘ (if rejected)
└────────┬────────┘
         │ (if approved)
         ▼
┌─────────────────┐
│ OrderGeneration │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OrderExecution  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Monitoring    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Complete     │
└─────────────────┘
"""
from typing import Optional, Callable, Dict
from loguru import logger

from autohedge.core.enums import TradingState, RiskDecision


class TradingStateMachine:
    """
    State machine for managing trading cycle transitions.
    
    Implements the state diagram with conditional transitions
    based on risk approval/rejection.
    """
    
    # Define valid state transitions
    TRANSITIONS: Dict[TradingState, list] = {
        TradingState.INITIALIZATION: [TradingState.THESIS_GENERATION],
        TradingState.THESIS_GENERATION: [TradingState.QUANT_ANALYSIS],
        TradingState.QUANT_ANALYSIS: [TradingState.RISK_ASSESSMENT],
        TradingState.RISK_ASSESSMENT: [
            TradingState.ORDER_GENERATION,  # if approved
            TradingState.THESIS_GENERATION,  # if rejected (retry)
        ],
        TradingState.ORDER_GENERATION: [TradingState.ORDER_EXECUTION],
        TradingState.ORDER_EXECUTION: [TradingState.MONITORING],
        TradingState.MONITORING: [
            TradingState.COMPLETE,
            TradingState.THESIS_GENERATION,  # new cycle
        ],
        TradingState.COMPLETE: [],  # Terminal state
    }
    
    def __init__(self, initial_state: TradingState = TradingState.INITIALIZATION):
        """
        Initialize the state machine.
        
        Args:
            initial_state: Initial state of the machine
        """
        self._state = initial_state
        self._history: list = [initial_state]
        self._on_transition: Optional[Callable] = None
        
        logger.info(f"State machine initialized: {self._state.value}")
    
    @property
    def state(self) -> TradingState:
        """Get current state."""
        return self._state
    
    @property
    def history(self) -> list:
        """Get state transition history."""
        return self._history.copy()
    
    def set_transition_callback(self, callback: Callable[[TradingState, TradingState], None]) -> None:
        """
        Set callback function for state transitions.
        
        Args:
            callback: Function called on each transition with (from_state, to_state)
        """
        self._on_transition = callback
    
    def can_transition_to(self, target: TradingState) -> bool:
        """
        Check if transition to target state is valid.
        
        Args:
            target: Target state to check
            
        Returns:
            True if transition is valid
        """
        return target in self.TRANSITIONS.get(self._state, [])
    
    def transition_to(self, target: TradingState) -> bool:
        """
        Transition to a new state.
        
        Args:
            target: Target state to transition to
            
        Returns:
            True if transition was successful
        """
        if not self.can_transition_to(target):
            logger.warning(
                f"Invalid transition: {self._state.value} -> {target.value}"
            )
            return False
        
        from_state = self._state
        self._state = target
        self._history.append(target)
        
        logger.info(f"State transition: {from_state.value} -> {target.value}")
        
        if self._on_transition:
            self._on_transition(from_state, target)
        
        return True
    
    def handle_risk_decision(self, decision: RiskDecision) -> TradingState:
        """
        Handle risk decision and determine next state.
        
        Args:
            decision: Risk decision (approved or rejected)
            
        Returns:
            Next state based on decision
        """
        if self._state != TradingState.RISK_ASSESSMENT:
            logger.warning("Risk decision called outside of RISK_ASSESSMENT state")
            return self._state
        
        if decision == RiskDecision.APPROVED:
            next_state = TradingState.ORDER_GENERATION
            logger.info("Risk APPROVED - proceeding to order generation")
        else:
            next_state = TradingState.THESIS_GENERATION
            logger.warning("Risk REJECTED - returning to thesis generation")
        
        self.transition_to(next_state)
        return next_state
    
    def reset(self) -> None:
        """Reset state machine to initial state."""
        self._state = TradingState.INITIALIZATION
        self._history = [TradingState.INITIALIZATION]
        logger.info("State machine reset")
    
    def is_complete(self) -> bool:
        """Check if state machine has reached complete state."""
        return self._state == TradingState.COMPLETE


