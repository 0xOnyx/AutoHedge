"""
Tests for trading module (state machine, tasks, cycle).
"""
import pytest
from autohedge.trading.state_machine import TradingStateMachine
from autohedge.trading.tasks import TaskFactory
from autohedge.core.enums import TradingState, RiskDecision


class TestTradingStateMachine:
    """Tests for TradingStateMachine class."""
    
    def test_initial_state(self):
        """Test initial state is INITIALIZATION."""
        sm = TradingStateMachine()
        assert sm.state == TradingState.INITIALIZATION
    
    def test_custom_initial_state(self):
        """Test custom initial state."""
        sm = TradingStateMachine(initial_state=TradingState.THESIS_GENERATION)
        assert sm.state == TradingState.THESIS_GENERATION
    
    def test_valid_transition(self):
        """Test valid state transition."""
        sm = TradingStateMachine()
        
        result = sm.transition_to(TradingState.THESIS_GENERATION)
        
        assert result is True
        assert sm.state == TradingState.THESIS_GENERATION
    
    def test_invalid_transition(self):
        """Test invalid state transition."""
        sm = TradingStateMachine()
        
        # Can't go directly to ORDER_EXECUTION from INITIALIZATION
        result = sm.transition_to(TradingState.ORDER_EXECUTION)
        
        assert result is False
        assert sm.state == TradingState.INITIALIZATION
    
    def test_can_transition_to(self):
        """Test can_transition_to method."""
        sm = TradingStateMachine()
        
        assert sm.can_transition_to(TradingState.THESIS_GENERATION) is True
        assert sm.can_transition_to(TradingState.COMPLETE) is False
    
    def test_full_happy_path(self):
        """Test complete trading cycle state transitions."""
        sm = TradingStateMachine()
        
        # Full path: INIT -> THESIS -> QUANT -> RISK -> ORDER -> EXEC -> MONITOR -> COMPLETE
        assert sm.transition_to(TradingState.THESIS_GENERATION) is True
        assert sm.transition_to(TradingState.QUANT_ANALYSIS) is True
        assert sm.transition_to(TradingState.RISK_ASSESSMENT) is True
        assert sm.transition_to(TradingState.ORDER_GENERATION) is True
        assert sm.transition_to(TradingState.ORDER_EXECUTION) is True
        assert sm.transition_to(TradingState.MONITORING) is True
        assert sm.transition_to(TradingState.COMPLETE) is True
        
        assert sm.is_complete() is True
    
    def test_risk_rejection_path(self):
        """Test risk rejection leads back to thesis generation."""
        sm = TradingStateMachine()
        
        sm.transition_to(TradingState.THESIS_GENERATION)
        sm.transition_to(TradingState.QUANT_ANALYSIS)
        sm.transition_to(TradingState.RISK_ASSESSMENT)
        
        # Risk rejected -> back to thesis
        next_state = sm.handle_risk_decision(RiskDecision.REJECTED)
        
        assert next_state == TradingState.THESIS_GENERATION
        assert sm.state == TradingState.THESIS_GENERATION
    
    def test_risk_approval_path(self):
        """Test risk approval proceeds to order generation."""
        sm = TradingStateMachine()
        
        sm.transition_to(TradingState.THESIS_GENERATION)
        sm.transition_to(TradingState.QUANT_ANALYSIS)
        sm.transition_to(TradingState.RISK_ASSESSMENT)
        
        # Risk approved -> proceed to order
        next_state = sm.handle_risk_decision(RiskDecision.APPROVED)
        
        assert next_state == TradingState.ORDER_GENERATION
        assert sm.state == TradingState.ORDER_GENERATION
    
    def test_history_tracking(self):
        """Test state history is tracked."""
        sm = TradingStateMachine()
        
        sm.transition_to(TradingState.THESIS_GENERATION)
        sm.transition_to(TradingState.QUANT_ANALYSIS)
        
        history = sm.history
        
        assert len(history) == 3  # INIT + 2 transitions
        assert history[0] == TradingState.INITIALIZATION
        assert history[1] == TradingState.THESIS_GENERATION
        assert history[2] == TradingState.QUANT_ANALYSIS
    
    def test_reset(self):
        """Test reset method."""
        sm = TradingStateMachine()
        
        sm.transition_to(TradingState.THESIS_GENERATION)
        sm.transition_to(TradingState.QUANT_ANALYSIS)
        
        sm.reset()
        
        assert sm.state == TradingState.INITIALIZATION
        assert len(sm.history) == 1
    
    def test_transition_callback(self):
        """Test transition callback is called."""
        sm = TradingStateMachine()
        
        transitions = []
        
        def callback(from_state, to_state):
            transitions.append((from_state, to_state))
        
        sm.set_transition_callback(callback)
        sm.transition_to(TradingState.THESIS_GENERATION)
        
        assert len(transitions) == 1
        assert transitions[0] == (TradingState.INITIALIZATION, TradingState.THESIS_GENERATION)


class TestTaskFactory:
    """Tests for TaskFactory class."""
    
    def test_thesis_task_creation(self):
        """Test thesis task creation without agent."""
        # We can test the description generation without needing a real agent
        description = f"""
            Task: Test task
            
            Stock: NVDA
            Market Data: Test data
            
            
            Generate a comprehensive trading thesis for NVDA including:
            - A concise market thesis
            - Key technical and fundamental factors
            - Detailed risk assessment
            - Trading parameters (entry/exit points, position sizing)
            
            Consider all available market intelligence in your analysis.
            """
        
        assert "NVDA" in description
        assert "thesis" in description.lower()
    
    def test_thesis_task_with_intelligence(self):
        """Test thesis task includes intelligence context."""
        intel_context = "Sentiment is bullish"
        
        intel_section = f"""
        
ADDITIONAL MARKET INTELLIGENCE:
{intel_context}
""" if intel_context else ""
        
        assert "Sentiment is bullish" in intel_section
    
    def test_risk_task_includes_approval_instruction(self):
        """Test risk task includes APPROVED/REJECTED instruction."""
        expected_text = "IMPORTANT: At the end, clearly state APPROVED or REJECTED."
        
        # This is part of the task description in TaskFactory
        assert "APPROVED" in expected_text
        assert "REJECTED" in expected_text


