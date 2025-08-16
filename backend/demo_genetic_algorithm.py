#!/usr/bin/env python3
"""
Demonstration of the Genetic Algorithm for Campaign Optimization
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.analytics_service import AnalyticsService


async def demonstrate_genetic_algorithm():
    print("=== Genetic Algorithm Campaign Optimization Demo ===\n")
    
    service = AnalyticsService()
    
    # 1. Configure genetic algorithm
    print("1. Configuring Genetic Algorithm")
    config = {
        "population_size": 20,
        "max_generations": 15,
        "crossover_rate": 0.85,
        "mutation_rate": 0.08,
        "tournament_size": 3,
        "elitism_rate": 0.15
    }
    await service.configure_genetic_algorithm(config)
    print(f"   ✓ Configured with population size: {config['population_size']}")
    print(f"   ✓ Max generations: {config['max_generations']}")
    print(f"   ✓ Crossover rate: {config['crossover_rate']}")
    print()
    
    # 2. Set optimization constraints
    print("2. Setting Optimization Constraints")
    constraints = {
        "max_cpc": {"min": 0.5, "max": 3.0},
        "daily_budget": {"min": 200.0, "max": 2000.0},
        "location_radius": {"min": 10.0, "max": 80.0}
    }
    await service.set_optimization_constraints(constraints)
    print(f"   ✓ Set constraints for {len(constraints)} parameters")
    print()
    
    # 3. Define sample campaigns
    print("3. Sample Campaign Data")
    campaigns = [
        {
            "name": "Premium Electronics",
            "historical_roi": 3.2,
            "historical_conversion_rate": 0.045,
            "historical_ctr": 0.012,
            "daily_budget": 800,
            "current_performance": 1200
        },
        {
            "name": "Fashion & Accessories",
            "historical_roi": 2.1,
            "historical_conversion_rate": 0.028,
            "historical_ctr": 0.008,
            "daily_budget": 600,
            "current_performance": 900
        },
        {
            "name": "Home & Garden",
            "historical_roi": 2.8,
            "historical_conversion_rate": 0.035,
            "historical_ctr": 0.010,
            "daily_budget": 500,
            "current_performance": 800
        }
    ]
    
    for i, campaign in enumerate(campaigns):
        print(f"   Campaign {i+1}: {campaign['name']}")
        print(f"      ROI: {campaign['historical_roi']:.1f}x")
        print(f"      Conversion Rate: {campaign['historical_conversion_rate']*100:.1f}%")
        print(f"      Current Budget: ${campaign['daily_budget']}")
    print()
    
    # 4. Test both optimization methods
    print("4. Comparing Optimization Methods")
    total_budget = 2500
    
    # Greedy optimization
    greedy_result = await service.optimize_budget_allocation(
        campaigns, total_budget, "maximize_roi", "greedy"
    )
    
    # Genetic optimization  
    genetic_result = await service.optimize_budget_allocation(
        campaigns, total_budget, "maximize_roi", "genetic"
    )
    
    print(f"   Total Budget: ${total_budget}")
    print(f"   Objective: Maximize ROI")
    print()
    
    print("   GREEDY ALGORITHM RESULTS:")
    print(f"      Expected Improvement: ${greedy_result.expected_improvement:.2f}")
    print(f"      Confidence Score: {greedy_result.confidence_score:.1%}")
    print(f"      Iterations: {greedy_result.iterations_used}")
    print("      Budget Allocation:")
    for param, value in greedy_result.optimized_parameters.items():
        campaign_idx = int(param.split("_")[1])
        campaign_name = campaigns[campaign_idx]["name"]
        print(f"         {campaign_name}: ${value}")
    print()
    
    print("   GENETIC ALGORITHM RESULTS:")
    print(f"      Expected Improvement: ${genetic_result.expected_improvement:.2f}")
    print(f"      Confidence Score: {genetic_result.confidence_score:.1%}")
    print(f"      Iterations: {genetic_result.iterations_used}")
    print(f"      Best Fitness: {genetic_result.metadata.get('best_fitness', 0):.2f}")
    print("      Budget Allocation:")
    for param, value in genetic_result.optimized_parameters.items():
        campaign_idx = int(param.split("_")[1])
        campaign_name = campaigns[campaign_idx]["name"]
        print(f"         {campaign_name}: ${value}")
    print()
    
    improvement_diff = genetic_result.expected_improvement - greedy_result.expected_improvement
    confidence_diff = genetic_result.confidence_score - greedy_result.confidence_score
    
    print("   COMPARISON SUMMARY:")
    print(f"      Improvement Difference: ${improvement_diff:.2f}")
    print(f"      Confidence Difference: {confidence_diff:.1%}")
    print(f"      Genetic Algorithm Better: {improvement_diff > 0}")
    print()
    
    # 5. Parameter optimization example
    print("5. Campaign Parameter Optimization")
    current_params = {
        "max_cpc": 1.2,
        "location_radius": 35.0,
        "daily_budget": 800.0
    }
    
    performance_history = [
        {"roi": 2.8, "conversion_rate": 0.032},
        {"roi": 3.1, "conversion_rate": 0.038},
        {"roi": 2.9, "conversion_rate": 0.035},
        {"roi": 3.3, "conversion_rate": 0.041}
    ]
    
    print("   Current Parameters:")
    for param, value in current_params.items():
        print(f"      {param}: {value}")
    print()
    
    result = await service.optimize_campaign_parameters(
        current_params, performance_history, "genetic"
    )
    
    print("   Optimized Parameters:")
    for param, value in result.optimized_parameters.items():
        print(f"      {param}: {value:.3f}")
    
    print(f"   Expected Improvement: ${result.expected_improvement:.2f}")
    print(f"   Confidence Score: {result.confidence_score:.1%}")
    print()
    
    # 6. Show genetic algorithm status
    print("6. Genetic Algorithm Status")
    status = await service.get_genetic_algorithm_status()
    print(f"   Configured: {status['configured']}")
    print(f"   Population Size: {status['config']['population_size']}")
    print(f"   Current Generation: {status['current_generation']}")
    print(f"   Best Fitness: {status['best_fitness']:.2f}")
    print(f"   Parameter Bounds: {status['parameter_bounds_count']} parameters")
    print(f"   Constraints: {status['constraints_count']} constraints")
    print()
    
    print("=== Demo Completed Successfully! ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_genetic_algorithm())