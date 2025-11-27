"""
Configuration module for the trading system.
Contains all configurable parameters and defaults.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Config:
    """
    Configuration for the AutoHedge trading system.
    
    Attributes:
        name: Name of the trading system
        description: Description of the trading system
        stocks: List of stock ticker symbols to analyze
        output_dir: Directory for storing outputs
        output_type: Type of output ("str", "list", "dict")
        max_retries: Maximum retries if risk is rejected
        llm_model: LLM model to use for agents
        verbose: Enable verbose logging
    """
    name: str = "autohedge"
    description: str = "fully autonomous hedge fund"
    stocks: List[str] = field(default_factory=list)
    output_dir: str = "outputs"
    output_type: str = "str"
    max_retries: int = 3
    llm_model: Optional[str] = None
    verbose: bool = True
    
    # LLM Model Options (for reference)
    SUPPORTED_MODELS = {
        "openai": ["gpt-4", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo"],
        "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-2"],
        "google": ["gemini-pro", "gemini-ultra"],
    }
    
    # Default model
    DEFAULT_MODEL = "gpt-4o-mini"
    
    def __post_init__(self):
        """Initialize configuration after dataclass creation."""
        if self.llm_model is None:
            self.llm_model = self.DEFAULT_MODEL
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(exist_ok=True)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create Config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

