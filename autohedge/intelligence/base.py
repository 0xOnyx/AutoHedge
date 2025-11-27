"""
Base classes for intelligence providers.
Defines the interface that all providers must implement.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class IntelligenceType(str, Enum):
    """Types of intelligence that can be provided."""
    SENTIMENT = "sentiment"
    MACRO = "macro"
    SECTOR = "sector"
    TECHNICAL = "technical"
    NEWS = "news"
    FUNDAMENTAL = "fundamental"
    OPTIONS = "options"
    INSIDER = "insider"
    INSTITUTIONAL = "institutional"
    CUSTOM = "custom"


@dataclass
class IntelligenceResult:
    """
    Result from an intelligence provider.
    
    Attributes:
        provider_name: Name of the provider that generated this result
        intelligence_type: Type of intelligence provided
        stock: Stock symbol analyzed
        data: Raw data from the analysis
        summary: Human-readable summary of findings
        confidence: Confidence score (0-1)
        risk_impact: Impact on risk assessment (-1 to 1, negative = higher risk)
        timestamp: When the analysis was performed
        metadata: Additional metadata
    """
    provider_name: str
    intelligence_type: IntelligenceType
    stock: str
    data: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    confidence: float = 0.5
    risk_impact: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_prompt_context(self) -> str:
        """Convert result to context string for LLM prompts."""
        return f"""
[{self.provider_name}] ({self.intelligence_type.value})
Summary: {self.summary}
Confidence: {self.confidence:.0%}
Risk Impact: {self.risk_impact:+.2f}
Details: {self.data}
"""


class IntelligenceProvider(ABC):
    """
    Abstract base class for intelligence providers.
    
    All intelligence providers must inherit from this class and implement
    the required methods. This ensures a consistent interface for the
    registry to work with.
    
    Example:
        class MyCustomProvider(IntelligenceProvider):
            @property
            def name(self) -> str:
                return "my_custom_provider"
            
            @property
            def intelligence_type(self) -> IntelligenceType:
                return IntelligenceType.CUSTOM
            
            def analyze(self, stock: str, context: dict) -> IntelligenceResult:
                # Your analysis logic here
                return IntelligenceResult(...)
    """
    
    def __init__(self, llm_model: Optional[str] = None):
        """
        Initialize the provider.
        
        Args:
            llm_model: Optional LLM model to use for AI-powered analysis
        """
        self.llm_model = llm_model
        self._enabled = True
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the provider."""
        pass
    
    @property
    @abstractmethod
    def intelligence_type(self) -> IntelligenceType:
        """Type of intelligence this provider offers."""
        pass
    
    @property
    def description(self) -> str:
        """Description of what this provider does."""
        return f"{self.name} intelligence provider"
    
    @property
    def enabled(self) -> bool:
        """Whether this provider is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable this provider."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable this provider."""
        self._enabled = False
    
    @abstractmethod
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """
        Perform analysis for a given stock.
        
        Args:
            stock: Stock ticker symbol
            context: Optional context from previous analyses
            
        Returns:
            IntelligenceResult with analysis findings
        """
        pass
    
    def validate_stock(self, stock: str) -> bool:
        """Validate if this provider can analyze the given stock."""
        return True  # Override in subclasses if needed


