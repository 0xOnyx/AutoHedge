"""
Intelligence registry module.
Manages registration and execution of intelligence providers.
"""
from typing import Dict, List, Optional, Any, Type
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


class IntelligenceRegistry:
    """
    Registry for managing intelligence providers.
    
    This class provides a centralized way to:
    - Register/unregister providers
    - Enable/disable providers
    - Gather insights from all providers
    - Aggregate results for risk assessment
    
    Usage:
        registry = IntelligenceRegistry()
        
        # Register providers
        registry.register(SentimentProvider())
        registry.register(MacroProvider())
        
        # Gather all insights for a stock
        insights = registry.gather_insights("NVDA")
        
        # Get aggregated context for prompts
        context = registry.get_aggregated_context("NVDA")
    """
    
    def __init__(self, parallel: bool = True, max_workers: int = 5):
        """
        Initialize the registry.
        
        Args:
            parallel: Whether to run providers in parallel
            max_workers: Maximum number of parallel workers
        """
        self._providers: Dict[str, IntelligenceProvider] = {}
        self.parallel = parallel
        self.max_workers = max_workers
        
        logger.info("IntelligenceRegistry initialized")
    
    def register(self, provider: IntelligenceProvider) -> "IntelligenceRegistry":
        """
        Register a provider.
        
        Args:
            provider: Provider instance to register
            
        Returns:
            Self for chaining
        """
        if provider.name in self._providers:
            logger.warning(f"Provider '{provider.name}' already registered, replacing")
        
        self._providers[provider.name] = provider
        logger.info(f"Registered provider: {provider.name} ({provider.intelligence_type.value})")
        return self
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a provider by name.
        
        Args:
            name: Name of provider to unregister
            
        Returns:
            True if provider was found and removed
        """
        if name in self._providers:
            del self._providers[name]
            logger.info(f"Unregistered provider: {name}")
            return True
        return False
    
    def get_provider(self, name: str) -> Optional[IntelligenceProvider]:
        """Get a provider by name."""
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())
    
    def list_enabled_providers(self) -> List[str]:
        """List all enabled provider names."""
        return [name for name, p in self._providers.items() if p.enabled]
    
    def enable_provider(self, name: str) -> bool:
        """Enable a provider by name."""
        if provider := self._providers.get(name):
            provider.enable()
            logger.info(f"Enabled provider: {name}")
            return True
        return False
    
    def disable_provider(self, name: str) -> bool:
        """Disable a provider by name."""
        if provider := self._providers.get(name):
            provider.disable()
            logger.info(f"Disabled provider: {name}")
            return True
        return False
    
    def gather_insights(
        self,
        stock: str,
        context: Optional[Dict[str, Any]] = None,
        types: Optional[List[IntelligenceType]] = None,
    ) -> List[IntelligenceResult]:
        """
        Gather insights from all enabled providers.
        
        Args:
            stock: Stock ticker symbol
            context: Optional context to pass to providers
            types: Optional filter for specific intelligence types
            
        Returns:
            List of IntelligenceResult from all providers
        """
        results: List[IntelligenceResult] = []
        enabled_providers = [
            p for p in self._providers.values()
            if p.enabled and p.validate_stock(stock)
            and (types is None or p.intelligence_type in types)
        ]
        
        if not enabled_providers:
            logger.warning("No enabled providers for gathering insights")
            return results
        
        if self.parallel and len(enabled_providers) > 1:
            results = self._gather_parallel(enabled_providers, stock, context)
        else:
            results = self._gather_sequential(enabled_providers, stock, context)
        
        logger.info(f"Gathered {len(results)} insights for {stock}")
        return results
    
    def _gather_sequential(
        self,
        providers: List[IntelligenceProvider],
        stock: str,
        context: Optional[Dict[str, Any]],
    ) -> List[IntelligenceResult]:
        """Gather insights sequentially."""
        results = []
        for provider in providers:
            try:
                result = provider.analyze(stock, context)
                results.append(result)
                logger.debug(f"Provider '{provider.name}' completed for {stock}")
            except Exception as e:
                logger.error(f"Provider '{provider.name}' failed: {str(e)}")
        return results
    
    def _gather_parallel(
        self,
        providers: List[IntelligenceProvider],
        stock: str,
        context: Optional[Dict[str, Any]],
    ) -> List[IntelligenceResult]:
        """Gather insights in parallel using ThreadPoolExecutor."""
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(provider.analyze, stock, context): provider
                for provider in providers
            }
            
            for future in as_completed(futures):
                provider = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.debug(f"Provider '{provider.name}' completed for {stock}")
                except Exception as e:
                    logger.error(f"Provider '{provider.name}' failed: {str(e)}")
        
        return results
    
    def get_aggregated_context(
        self,
        stock: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get aggregated context string for LLM prompts.
        
        Args:
            stock: Stock ticker symbol
            context: Optional context to pass to providers
            
        Returns:
            Aggregated context string from all providers
        """
        insights = self.gather_insights(stock, context)
        
        if not insights:
            return "No additional market intelligence available."
        
        sections = []
        for insight in insights:
            sections.append(insight.to_prompt_context())
        
        return "\n".join([
            "=" * 50,
            "ADDITIONAL MARKET INTELLIGENCE",
            "=" * 50,
            *sections,
            "=" * 50,
        ])
    
    def get_risk_adjustment(self, stock: str) -> float:
        """
        Calculate aggregate risk adjustment from all providers.
        
        Args:
            stock: Stock ticker symbol
            
        Returns:
            Weighted average risk impact (-1 to 1)
        """
        insights = self.gather_insights(stock)
        
        if not insights:
            return 0.0
        
        total_weight = sum(i.confidence for i in insights)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(i.risk_impact * i.confidence for i in insights)
        return weighted_sum / total_weight
    
    def clear(self) -> None:
        """Clear all registered providers."""
        self._providers.clear()
        logger.info("Registry cleared")


