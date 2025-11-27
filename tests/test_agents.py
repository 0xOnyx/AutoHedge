"""
Tests for agents module (factory, prompts).
"""
import pytest
from autohedge.agents.factory import AgentFactory
from autohedge.agents.prompts import (
    DIRECTOR_PROMPT,
    QUANT_PROMPT,
    RISK_PROMPT,
    EXECUTION_PROMPT,
    AgentPrompt,
)


class TestAgentPrompts:
    """Tests for agent prompts."""
    
    def test_director_prompt(self):
        """Test Director prompt configuration."""
        assert DIRECTOR_PROMPT.role == "Trading Director"
        assert "orchestrate" in DIRECTOR_PROMPT.goal.lower()
        assert len(DIRECTOR_PROMPT.backstory) > 100
    
    def test_quant_prompt(self):
        """Test Quant prompt configuration."""
        assert QUANT_PROMPT.role == "Quantitative Analyst"
        assert "numerical" in QUANT_PROMPT.goal.lower() or "analysis" in QUANT_PROMPT.goal.lower()
        assert len(QUANT_PROMPT.backstory) > 100
    
    def test_risk_prompt(self):
        """Test Risk prompt configuration."""
        assert RISK_PROMPT.role == "Risk Manager"
        assert "risk" in RISK_PROMPT.goal.lower()
        assert "APPROVED" in RISK_PROMPT.backstory or "REJECTED" in RISK_PROMPT.backstory
    
    def test_execution_prompt(self):
        """Test Execution prompt configuration."""
        assert EXECUTION_PROMPT.role == "Execution Agent"
        assert "execute" in EXECUTION_PROMPT.goal.lower() or "trade" in EXECUTION_PROMPT.goal.lower()
        assert len(EXECUTION_PROMPT.backstory) > 100
    
    def test_agent_prompt_dataclass(self):
        """Test AgentPrompt dataclass."""
        prompt = AgentPrompt(
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory",
        )
        
        assert prompt.role == "Test Role"
        assert prompt.goal == "Test Goal"
        assert prompt.backstory == "Test Backstory"


class TestAgentFactory:
    """Tests for AgentFactory class."""
    
    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = AgentFactory(llm_model="gpt-4o-mini", verbose=False)
        
        assert factory.llm_model == "gpt-4o-mini"
        assert factory.verbose is False
    
    def test_factory_default_initialization(self):
        """Test factory default initialization."""
        factory = AgentFactory()
        
        assert factory.llm_model is None
        assert factory.verbose is True
    
    def test_get_agent_kwargs(self):
        """Test _get_agent_kwargs method."""
        factory = AgentFactory(llm_model="gpt-4", verbose=True)
        kwargs = factory._get_agent_kwargs()
        
        assert kwargs["verbose"] is True
        assert kwargs["allow_delegation"] is False
        assert kwargs["llm"] == "gpt-4"
    
    def test_get_agent_kwargs_no_llm(self):
        """Test _get_agent_kwargs without LLM model."""
        factory = AgentFactory(llm_model=None)
        kwargs = factory._get_agent_kwargs()
        
        assert "llm" not in kwargs
    
    @pytest.mark.skip(reason="Requires CrewAI Agent instantiation which needs more setup")
    def test_director_property(self):
        """Test director property creates agent."""
        factory = AgentFactory(llm_model="gpt-4o-mini")
        director = factory.director
        
        assert director is not None
        assert director.role == "Trading Director"
    
    @pytest.mark.skip(reason="Requires CrewAI Agent instantiation which needs more setup")
    def test_agent_caching(self):
        """Test that agents are cached."""
        factory = AgentFactory(llm_model="gpt-4o-mini")
        
        director1 = factory.director
        director2 = factory.director
        
        assert director1 is director2

