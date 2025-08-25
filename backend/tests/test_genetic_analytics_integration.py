"""
Integration tests for genetic algorithm in analytics service.
"""

import pytest
import sys
import os
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.analytics_service import AnalyticsService


class TestGeneticAnalyticsService:
    """Test cases for genetic algorithm integration in AnalyticsService."""
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance for testing."""
        return AnalyticsService()
    
    @pytest.fixture
    def sample_campaigns(self):
        """Sample campaigns for testing."""
        return [
            {
                "historical_roi": 2.5,
                "historical_conversion_rate": 0.03,
                "historical_ctr": 0.01,
                "daily_budget": 1000,
                "optimal_cpc": 1.5,
                "optimal_radius": 30
            },
            {
                "historical_roi": 1.8,
                "historical_conversion_rate": 0.02,
                "historical_ctr": 0.008,
                "daily_budget": 800,
                "optimal_cpc": 1.2,
                "optimal_radius": 25
            }
        ]
    
    @pytest.fixture
    def sample_constraints(self):
        """Sample constraints for testing."""
        return {
            "max_cpc": {"min": 0.1, "max": 5.0},
            "daily_budget": {"min": 100.0, "max": 5000.0},
            "location_radius": {"min": 5.0, "max": 100.0}
        }
    
    @pytest.mark.asyncio
    async def test_configure_genetic_algorithm(self, analytics_service):
        """Test genetic algorithm configuration."""
        config = {
            "population_size": 20,
            "max_generations": 10,
            "crossover_rate": 0.9,
            "mutation_rate": 0.05,
            "tournament_size": 2
        }
        
        success = await analytics_service.configure_genetic_algorithm(config)
        assert success
        
        # Verify configuration was applied
        status = await analytics_service.get_genetic_algorithm_status()
        assert status["configured"]
        assert status["config"]["population_size"] == 20
        assert status["config"]["max_generations"] == 10
        assert status["config"]["crossover_rate"] == 0.9
    
    @pytest.mark.asyncio
    async def test_set_optimization_constraints(self, analytics_service, sample_constraints):
        """Test setting optimization constraints."""
        success = await analytics_service.set_optimization_constraints(sample_constraints)
        assert success
        
        # Verify constraints were set
        status = await analytics_service.get_genetic_algorithm_status()
        assert status["parameter_bounds_count"] == len(sample_constraints)
        assert status["constraints_count"] == len(sample_constraints)
    
    @pytest.mark.asyncio
    async def test_budget_optimization_genetic_method(self, analytics_service, sample_campaigns):
        """Test budget optimization using genetic algorithm."""
        # Configure genetic algorithm for faster testing
        config = {
            "population_size": 10,
            "max_generations": 5,
            "max_stagnant_generations": 3
        }
        await analytics_service.configure_genetic_algorithm(config)
        
        result = await analytics_service.optimize_budget_allocation(
            sample_campaigns, 2000, "maximize_roi", "genetic"
        )
        
        assert result.optimization_method == "genetic_algorithm"
        assert result.expected_improvement >= 0
        assert result.confidence_score > 0
        assert "campaign_0_budget" in result.optimized_parameters
        assert "campaign_1_budget" in result.optimized_parameters
        
        # Check budget allocation sums to total
        total_allocated = sum(result.optimized_parameters.values())
        assert abs(total_allocated - 2000) < 1.0
    
    @pytest.mark.asyncio
    async def test_parameter_optimization_genetic_method(self, analytics_service):
        """Test campaign parameter optimization using genetic algorithm."""
        # Configure genetic algorithm for faster testing
        config = {
            "population_size": 10,
            "max_generations": 5
        }
        await analytics_service.configure_genetic_algorithm(config)
        
        current_params = {
            "max_cpc": 1.0,
            "location_radius": 25.0,
            "daily_budget": 1000.0
        }
        
        performance_history = [
            {"roi": 2.5, "conversion_rate": 0.03},
            {"roi": 2.2, "conversion_rate": 0.025},
            {"roi": 2.8, "conversion_rate": 0.035}
        ]
        
        result = await analytics_service.optimize_campaign_parameters(
            current_params, performance_history, "genetic"
        )
        
        assert result.optimization_method == "genetic_algorithm"
        assert result.expected_improvement >= 0
        assert "max_cpc" in result.optimized_parameters
        assert "location_radius" in result.optimized_parameters
        assert "daily_budget" in result.optimized_parameters
    
    @pytest.mark.asyncio
    async def test_genetic_algorithm_status(self, analytics_service):
        """Test getting genetic algorithm status."""
        # Initial status should show not configured (new instance)
        status = await analytics_service.get_genetic_algorithm_status()
        assert "configured" in status
        assert "config" in status
        assert "timestamp" in status
        
        # Configure and check status again
        config = {"population_size": 15, "max_generations": 8}
        await analytics_service.configure_genetic_algorithm(config)
        
        status = await analytics_service.get_genetic_algorithm_status()
        assert status["configured"]
        assert status["config"]["population_size"] == 15
        assert status["config"]["max_generations"] == 8
    
    @pytest.mark.asyncio
    async def test_optimization_comparison(self, analytics_service, sample_campaigns):
        """Test comparing greedy vs genetic optimization methods."""
        # Configure genetic algorithm for faster testing
        config = {
            "population_size": 8,
            "max_generations": 3
        }
        await analytics_service.configure_genetic_algorithm(config)
        
        comparison = await analytics_service.get_optimization_comparison(
            sample_campaigns, 2000, "maximize_roi"
        )
        
        assert "greedy" in comparison
        assert "genetic" in comparison
        assert "comparison" in comparison
        
        # Check greedy results
        greedy = comparison["greedy"]
        assert "optimized_parameters" in greedy
        assert "expected_improvement" in greedy
        assert "confidence_score" in greedy
        
        # Check genetic results
        genetic = comparison["genetic"]
        assert "optimized_parameters" in genetic
        assert "expected_improvement" in genetic
        assert "confidence_score" in genetic
        
        # Check comparison metrics
        comp = comparison["comparison"]
        assert "improvement_difference" in comp
        assert "confidence_difference" in comp
        assert "genetic_better" in comp
        assert "genetic_more_confident" in comp
    
    @pytest.mark.asyncio
    async def test_different_objectives(self, analytics_service, sample_campaigns):
        """Test genetic optimization with different objectives."""
        config = {
            "population_size": 5,
            "max_generations": 3
        }
        await analytics_service.configure_genetic_algorithm(config)
        
        objectives = ["maximize_roi", "maximize_conversions", "maximize_clicks", "combined"]
        
        for objective in objectives:
            result = await analytics_service.optimize_budget_allocation(
                sample_campaigns, 1500, objective, "genetic"
            )
            
            assert result.optimization_method == "genetic_algorithm"
            assert result.expected_improvement >= 0
            assert objective in result.metadata.get("objective", "")
    
    @pytest.mark.asyncio
    async def test_constraints_with_genetic_optimization(self, analytics_service, sample_campaigns, sample_constraints):
        """Test genetic optimization with constraints."""
        # Set constraints
        await analytics_service.set_optimization_constraints(sample_constraints)
        
        # Configure genetic algorithm
        config = {
            "population_size": 8,
            "max_generations": 4
        }
        await analytics_service.configure_genetic_algorithm(config)
        
        result = await analytics_service.optimize_budget_allocation(
            sample_campaigns, 2000, "maximize_roi", "genetic"
        )
        
        assert result.optimization_method == "genetic_algorithm"
        assert result.expected_improvement >= 0
        
        # Verify budget allocation respects constraints
        total_allocated = sum(result.optimized_parameters.values())
        assert abs(total_allocated - 2000) < 1.0
    
    @pytest.mark.asyncio
    async def test_invalid_configuration(self, analytics_service):
        """Test handling of invalid genetic algorithm configuration."""
        # Test with invalid config (should not crash)
        config = {
            "population_size": -1,  # Invalid
            "max_generations": 0,   # Invalid
            "crossover_rate": 2.0   # Invalid (should be 0-1)
        }
        
        # Should handle gracefully and not crash
        try:
            success = await analytics_service.configure_genetic_algorithm(config)
            # Should either succeed (with correction) or fail gracefully
            assert isinstance(success, bool)
        except Exception:
            # If it raises an exception, it should be a controlled one
            pass
    
    @pytest.mark.asyncio
    async def test_empty_campaigns_genetic(self, analytics_service):
        """Test genetic optimization with empty campaigns list."""
        config = {"population_size": 5, "max_generations": 2}
        await analytics_service.configure_genetic_algorithm(config)
        
        with pytest.raises(Exception):  # Should raise an exception
            await analytics_service.optimize_budget_allocation(
                [], 1000, "maximize_roi", "genetic"
            )
    
    @pytest.mark.asyncio
    async def test_genetic_vs_greedy_performance(self, analytics_service, sample_campaigns):
        """Test that genetic algorithm finds competitive or better solutions than greedy."""
        # Configure genetic algorithm for more thorough search
        config = {
            "population_size": 20,
            "max_generations": 15,
            "max_stagnant_generations": 5
        }
        await analytics_service.configure_genetic_algorithm(config)
        
        # Run both optimizations
        greedy_result = await analytics_service.optimize_budget_allocation(
            sample_campaigns, 2000, "maximize_roi", "greedy"
        )
        
        genetic_result = await analytics_service.optimize_budget_allocation(
            sample_campaigns, 2000, "maximize_roi", "genetic"
        )
        
        # Genetic algorithm should be competitive (not necessarily always better due to randomness,
        # but should be in the same ballpark or better)
        improvement_ratio = genetic_result.expected_improvement / max(greedy_result.expected_improvement, 1)
        
        # Allow for some variation, but genetic should be reasonably competitive
        assert improvement_ratio >= 0.8  # At least 80% as good as greedy
        
        # Genetic algorithm should generally have higher confidence due to more thorough search
        assert genetic_result.confidence_score >= greedy_result.confidence_score - 0.1


if __name__ == "__main__":
    # Run a simple test to verify everything works
    async def simple_test():
        service = AnalyticsService()
        
        # Test configuration
        config = {"population_size": 10, "max_generations": 3}
        success = await service.configure_genetic_algorithm(config)
        print(f"Configuration test: {'PASS' if success else 'FAIL'}")
        
        # Test optimization
        campaigns = [{"historical_roi": 2.0, "historical_conversion_rate": 0.02}]
        result = await service.optimize_budget_allocation(campaigns, 1000, "maximize_roi", "genetic")
        print(f"Optimization test: {'PASS' if result.optimization_method == 'genetic_algorithm' else 'FAIL'}")
        
        print("Simple integration test completed!")
    
    asyncio.run(simple_test())