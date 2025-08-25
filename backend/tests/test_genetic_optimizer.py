"""
Unit tests for genetic optimizer module.
"""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.analytics.genetic_optimizer import (
    GeneticOptimizer, 
    GeneticConfig, 
    Chromosome,
    OptimizationResult
)


class TestChromosome:
    """Test cases for Chromosome class."""
    
    def test_chromosome_initialization(self):
        """Test chromosome initialization."""
        genes = {"param1": 1.0, "param2": 2.0}
        bounds = {"param1": (0.0, 2.0), "param2": (1.0, 3.0)}
        
        chromosome = Chromosome(genes, bounds)
        
        assert chromosome.genes == genes
        assert chromosome.parameter_bounds == bounds
        assert chromosome.fitness == 0.0
        assert not chromosome.evaluated
    
    def test_chromosome_validation(self):
        """Test gene validation with bounds."""
        genes = {"param1": -1.0, "param2": 5.0}  # Out of bounds
        bounds = {"param1": (0.0, 2.0), "param2": (1.0, 3.0)}
        
        chromosome = Chromosome(genes, bounds)
        chromosome.validate_genes()
        
        assert chromosome.genes["param1"] == 0.0  # Clipped to min
        assert chromosome.genes["param2"] == 3.0  # Clipped to max
    
    def test_chromosome_copy(self):
        """Test chromosome copying."""
        genes = {"param1": 1.0, "param2": 2.0}
        bounds = {"param1": (0.0, 2.0), "param2": (1.0, 3.0)}
        
        original = Chromosome(genes, bounds)
        original.fitness = 10.0
        original.evaluated = True
        
        copy = original.copy()
        
        assert copy.genes == original.genes
        assert copy.genes is not original.genes  # Different objects
        assert copy.fitness == original.fitness
        assert copy.evaluated == original.evaluated


class TestGeneticConfig:
    """Test cases for GeneticConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GeneticConfig()
        
        assert config.population_size == 50
        assert config.max_generations == 100
        assert config.crossover_rate == 0.8
        assert config.mutation_rate == 0.1
        assert config.tournament_size == 3
        assert config.elitism_rate == 0.1
        assert config.convergence_threshold == 1e-6
        assert config.max_stagnant_generations == 20
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = GeneticConfig(
            population_size=30,
            max_generations=50,
            crossover_rate=0.9,
            mutation_rate=0.15
        )
        
        assert config.population_size == 30
        assert config.max_generations == 50
        assert config.crossover_rate == 0.9
        assert config.mutation_rate == 0.15


class TestGeneticOptimizer:
    """Test cases for GeneticOptimizer class."""
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        optimizer = GeneticOptimizer()
        
        assert isinstance(optimizer.config, GeneticConfig)
        assert optimizer.population == []
        assert optimizer.best_chromosome is None
        assert optimizer.generation == 0
        assert optimizer.fitness_history == []
        assert optimizer.parameter_bounds == {}
        assert optimizer.constraints == {}
    
    def test_set_parameter_bounds(self):
        """Test setting parameter bounds."""
        optimizer = GeneticOptimizer()
        bounds = {"param1": (0.0, 10.0), "param2": (5.0, 15.0)}
        
        optimizer.set_parameter_bounds(bounds)
        
        assert optimizer.parameter_bounds == bounds
    
    def test_set_constraints(self):
        """Test setting constraints."""
        optimizer = GeneticOptimizer()
        constraints = {
            "param1": {"min": 0.0, "max": 10.0},
            "param2": {"min": 5.0, "max": 15.0}
        }
        
        optimizer.set_constraints(constraints)
        
        assert optimizer.constraints == constraints
        assert "param1" in optimizer.parameter_bounds
        assert "param2" in optimizer.parameter_bounds
        assert optimizer.parameter_bounds["param1"] == (0.0, 10.0)
        assert optimizer.parameter_bounds["param2"] == (5.0, 15.0)
    
    def test_initialize_population(self):
        """Test population initialization."""
        optimizer = GeneticOptimizer()
        optimizer.config.population_size = 10
        
        bounds = {"param1": (0.0, 10.0), "param2": (5.0, 15.0)}
        optimizer.set_parameter_bounds(bounds)
        
        template = {"param1": 5.0, "param2": 10.0}
        population = optimizer.initialize_population(template)
        
        assert len(population) == 10
        for chromosome in population:
            assert isinstance(chromosome, Chromosome)
            assert "param1" in chromosome.genes
            assert "param2" in chromosome.genes
            assert 0.0 <= chromosome.genes["param1"] <= 10.0
            assert 5.0 <= chromosome.genes["param2"] <= 15.0
    
    def test_evaluate_fitness(self):
        """Test fitness evaluation."""
        optimizer = GeneticOptimizer()
        
        genes = {"campaign_0_budget": 1000.0, "max_cpc": 1.5}
        chromosome = Chromosome(genes, {})
        
        campaigns = [
            {
                "historical_roi": 2.5,
                "historical_conversion_rate": 0.03,
                "historical_ctr": 0.01,
                "daily_budget": 1000,
                "optimal_cpc": 1.5,
                "optimal_radius": 30
            }
        ]
        
        fitness = optimizer.evaluate_fitness(chromosome, campaigns, "maximize_roi")
        
        assert fitness > 0
        assert chromosome.fitness == fitness
        assert chromosome.evaluated
    
    def test_tournament_selection(self):
        """Test tournament selection."""
        optimizer = GeneticOptimizer()
        optimizer.config.tournament_size = 3
        
        # Create population with different fitness values
        population = []
        for i in range(5):
            genes = {"param1": float(i)}
            chromosome = Chromosome(genes, {})
            chromosome.fitness = float(i)  # Fitness 0, 1, 2, 3, 4
            population.append(chromosome)
        
        selected = optimizer.tournament_selection(population)
        
        # Should select one of the higher fitness chromosomes more often
        assert selected in population
        assert selected.fitness >= 0
    
    def test_single_point_crossover(self):
        """Test single-point crossover."""
        optimizer = GeneticOptimizer()
        optimizer.config.crossover_rate = 1.0  # Always crossover for testing
        
        genes1 = {"param1": 1.0, "param2": 2.0, "param3": 3.0}
        genes2 = {"param1": 4.0, "param2": 5.0, "param3": 6.0}
        
        parent1 = Chromosome(genes1, {})
        parent2 = Chromosome(genes2, {})
        
        offspring1, offspring2 = optimizer.single_point_crossover(parent1, parent2)
        
        assert isinstance(offspring1, Chromosome)
        assert isinstance(offspring2, Chromosome)
        
        # Offspring should have genes from both parents
        all_parent_values = set(genes1.values()) | set(genes2.values())
        offspring1_values = set(offspring1.genes.values())
        offspring2_values = set(offspring2.genes.values())
        
        assert offspring1_values.issubset(all_parent_values)
        assert offspring2_values.issubset(all_parent_values)
    
    def test_two_point_crossover(self):
        """Test two-point crossover."""
        optimizer = GeneticOptimizer()
        optimizer.config.crossover_rate = 1.0  # Always crossover for testing
        
        genes1 = {"param1": 1.0, "param2": 2.0, "param3": 3.0, "param4": 4.0}
        genes2 = {"param1": 5.0, "param2": 6.0, "param3": 7.0, "param4": 8.0}
        
        parent1 = Chromosome(genes1, {})
        parent2 = Chromosome(genes2, {})
        
        offspring1, offspring2 = optimizer.two_point_crossover(parent1, parent2)
        
        assert isinstance(offspring1, Chromosome)
        assert isinstance(offspring2, Chromosome)
        
        # Offspring should have genes from both parents
        all_parent_values = set(genes1.values()) | set(genes2.values())
        offspring1_values = set(offspring1.genes.values())
        offspring2_values = set(offspring2.genes.values())
        
        assert offspring1_values.issubset(all_parent_values)
        assert offspring2_values.issubset(all_parent_values)
    
    def test_mutation(self):
        """Test mutation operation."""
        optimizer = GeneticOptimizer()
        optimizer.config.mutation_rate = 1.0  # Always mutate for testing
        
        bounds = {"param1": (0.0, 10.0), "param2": (5.0, 15.0)}
        optimizer.set_parameter_bounds(bounds)
        
        genes = {"param1": 5.0, "param2": 10.0}
        original = Chromosome(genes, bounds)
        
        mutated = optimizer.mutate(original)
        
        assert isinstance(mutated, Chromosome)
        assert mutated is not original  # Different objects
        assert not mutated.evaluated  # Should reset evaluation flag
        
        # Genes should be within bounds
        assert 0.0 <= mutated.genes["param1"] <= 10.0
        assert 5.0 <= mutated.genes["param2"] <= 15.0
    
    def test_get_elite(self):
        """Test elite selection."""
        optimizer = GeneticOptimizer()
        optimizer.config.elitism_rate = 0.4  # 40% elite
        
        # Create population with different fitness values
        population = []
        for i in range(10):
            genes = {"param1": float(i)}
            chromosome = Chromosome(genes, {})
            chromosome.fitness = float(i)  # Fitness 0-9
            population.append(chromosome)
        
        elite = optimizer.get_elite(population)
        
        expected_elite_count = max(1, int(10 * 0.4))  # 4 chromosomes
        assert len(elite) == expected_elite_count
        
        # Elite should be the highest fitness chromosomes
        elite_fitness = [c.fitness for c in elite]
        assert elite_fitness == sorted(elite_fitness, reverse=True)
        assert max(elite_fitness) == 9.0  # Highest fitness
    
    def test_optimize_budget_allocation(self):
        """Test budget optimization with genetic algorithm."""
        optimizer = GeneticOptimizer()
        optimizer.config.population_size = 10
        optimizer.config.max_generations = 5  # Short run for testing
        
        campaigns = [
            {"historical_roi": 2.5, "historical_conversion_rate": 0.03, "daily_budget": 1000},
            {"historical_roi": 1.8, "historical_conversion_rate": 0.02, "daily_budget": 800}
        ]
        
        result = optimizer.optimize_budget_allocation(campaigns, 2000, "maximize_roi")
        
        assert isinstance(result, OptimizationResult)
        assert result.optimization_method == "genetic_algorithm"
        assert result.expected_improvement >= 0
        assert "campaign_0_budget" in result.optimized_parameters
        assert "campaign_1_budget" in result.optimized_parameters
        
        # Check budget allocation sums to total
        total_allocated = (result.optimized_parameters["campaign_0_budget"] + 
                         result.optimized_parameters["campaign_1_budget"])
        assert abs(total_allocated - 2000) < 1.0  # Allow small rounding error
    
    def test_optimize_campaign_parameters(self):
        """Test campaign parameter optimization."""
        optimizer = GeneticOptimizer()
        optimizer.config.population_size = 10
        optimizer.config.max_generations = 5  # Short run for testing
        
        current_params = {
            "max_cpc": 1.0,
            "location_radius": 25.0,
            "daily_budget": 1000.0
        }
        
        performance_history = [
            {"roi": 2.5, "conversion_rate": 0.03},
            {"roi": 2.2, "conversion_rate": 0.025}
        ]
        
        result = optimizer.optimize_campaign_parameters(current_params, performance_history)
        
        assert isinstance(result, OptimizationResult)
        assert result.optimization_method == "genetic_algorithm"
        assert result.expected_improvement >= 0
        assert "max_cpc" in result.optimized_parameters
        assert "location_radius" in result.optimized_parameters
        assert "daily_budget" in result.optimized_parameters
        
        # Parameters should be within reasonable bounds
        assert 0.1 <= result.optimized_parameters["max_cpc"] <= 5.0
        assert 5.0 <= result.optimized_parameters["location_radius"] <= 100.0
        assert 50.0 <= result.optimized_parameters["daily_budget"] <= 5000.0
    
    def test_empty_campaigns_list(self):
        """Test handling of empty campaigns list."""
        optimizer = GeneticOptimizer()
        
        with pytest.raises(ValueError):
            optimizer.optimize_budget_allocation([], 1000)
    
    def test_zero_budget(self):
        """Test handling of zero budget."""
        optimizer = GeneticOptimizer()
        campaigns = [{"historical_roi": 2.0, "historical_conversion_rate": 0.02}]
        
        # Should not crash with zero budget
        result = optimizer.optimize_budget_allocation(campaigns, 0)
        assert isinstance(result, OptimizationResult)
    
    def test_single_campaign(self):
        """Test optimization with single campaign."""
        optimizer = GeneticOptimizer()
        optimizer.config.population_size = 5
        optimizer.config.max_generations = 3
        
        campaigns = [{"historical_roi": 2.5, "historical_conversion_rate": 0.03}]
        
        result = optimizer.optimize_budget_allocation(campaigns, 1000)
        
        assert isinstance(result, OptimizationResult)
        assert "campaign_0_budget" in result.optimized_parameters
        assert result.optimized_parameters["campaign_0_budget"] == 1000.0
    
    def test_different_objectives(self):
        """Test optimization with different objectives."""
        optimizer = GeneticOptimizer()
        optimizer.config.population_size = 5
        optimizer.config.max_generations = 3
        
        campaigns = [
            {"historical_roi": 2.5, "historical_conversion_rate": 0.03, "historical_ctr": 0.01}
        ]
        
        # Test different objectives
        objectives = ["maximize_roi", "maximize_conversions", "maximize_clicks", "combined"]
        
        for objective in objectives:
            result = optimizer.optimize_budget_allocation(campaigns, 1000, objective)
            assert isinstance(result, OptimizationResult)
            assert result.optimized_parameters["campaign_0_budget"] == 1000.0
    
    def test_convergence_detection(self):
        """Test convergence detection mechanisms."""
        optimizer = GeneticOptimizer()
        optimizer.config.population_size = 5
        optimizer.config.max_generations = 100
        optimizer.config.max_stagnant_generations = 5  # Quick convergence
        
        campaigns = [{"historical_roi": 2.5, "historical_conversion_rate": 0.03}]
        
        result = optimizer.optimize_budget_allocation(campaigns, 1000)
        
        # Should converge before max generations
        assert result.iterations_used < 100
        assert "convergence_reason" in result.metadata


if __name__ == "__main__":
    pytest.main([__file__])