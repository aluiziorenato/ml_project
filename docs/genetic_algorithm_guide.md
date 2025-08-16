# Simple Genetic Algorithm (SGA) for Campaign Optimization

This document describes the implementation and usage of the Simple Genetic Algorithm (SGA) for optimizing campaign parameters in the Mercado Livre ML automation system.

## Overview

The SGA implementation provides an advanced optimization method that can find better solutions than traditional greedy algorithms, especially for complex optimization problems with multiple interdependent parameters.

## Key Features

### 1. Chromosome Representation
- **Genes**: Campaign parameters encoded as floating-point values
- **Parameters**: Budget allocation, bidding (max_cpc, target_cpa), targeting (location_radius, audience_expansion)
- **Bounds**: Configurable min/max constraints for each parameter
- **Validation**: Automatic clipping to ensure parameters stay within valid ranges

### 2. Selection Methods
- **Tournament Selection**: Selects parents based on fitness competition
- **Configurable Tournament Size**: Default 3, can be adjusted
- **Elite Preservation**: Best chromosomes automatically survive to next generation

### 3. Crossover Operations
- **Single-Point Crossover**: Exchanges genes at one random point
- **Two-Point Crossover**: Exchanges genes between two random points
- **Adaptive Selection**: Automatically chooses crossover type
- **Configurable Rate**: Default 80% crossover rate

### 4. Mutation Operations
- **Gaussian Mutation**: Small random changes based on parameter bounds
- **Configurable Rate**: Default 10% mutation rate
- **Bounded Mutation**: Ensures mutated values stay within constraints

### 5. Fitness Evaluation
- **Multi-Objective**: Supports ROI, conversions, clicks, and combined objectives
- **Performance Metrics**: Based on CTR, conversion rate, and ROI
- **Campaign Modeling**: Considers budget, bidding, and targeting effects
- **Constraint Penalties**: Penalizes solutions that violate constraints

### 6. Elitism Strategy
- **Configurable Elite Rate**: Default 10% of population preserved
- **Best Solution Tracking**: Always maintains the best solution found
- **Convergence Detection**: Stops when no improvement for specified generations

## Configuration Parameters

```python
class GeneticConfig:
    population_size: int = 50           # Number of solutions in each generation
    max_generations: int = 100          # Maximum number of generations
    crossover_rate: float = 0.8         # Probability of crossover (0-1)
    mutation_rate: float = 0.1          # Probability of mutation (0-1)
    tournament_size: int = 3            # Number of candidates in tournament selection
    elitism_rate: float = 0.1           # Fraction of population to preserve (0-1)
    convergence_threshold: float = 1e-6 # Minimum improvement threshold
    max_stagnant_generations: int = 20  # Stop if no improvement for this many generations
```

## Usage Examples

### 1. Basic Budget Optimization

```python
from core.analytics.genetic_optimizer import GeneticOptimizer, GeneticConfig

# Configure the genetic algorithm
config = GeneticConfig(
    population_size=30,
    max_generations=50,
    crossover_rate=0.8,
    mutation_rate=0.1
)

# Create optimizer
optimizer = GeneticOptimizer(config)

# Define campaigns
campaigns = [
    {
        "historical_roi": 2.5,
        "historical_conversion_rate": 0.03,
        "historical_ctr": 0.01,
        "daily_budget": 1000
    },
    {
        "historical_roi": 1.8,
        "historical_conversion_rate": 0.02,
        "historical_ctr": 0.008,
        "daily_budget": 800
    }
]

# Optimize budget allocation
result = optimizer.optimize_budget_allocation(
    campaigns=campaigns,
    total_budget=2000,
    objective="maximize_roi"
)

print(f"Optimized allocation: {result.optimized_parameters}")
print(f"Expected improvement: {result.expected_improvement}")
```

### 2. Campaign Parameter Optimization

```python
# Define current parameters
current_params = {
    "max_cpc": 1.0,
    "location_radius": 25.0,
    "daily_budget": 1000.0,
    "target_cpa": 50.0
}

# Define performance history
performance_history = [
    {"roi": 2.5, "conversion_rate": 0.03, "ctr": 0.01},
    {"roi": 2.2, "conversion_rate": 0.025, "ctr": 0.009},
    {"roi": 2.8, "conversion_rate": 0.035, "ctr": 0.011}
]

# Optimize parameters
result = optimizer.optimize_campaign_parameters(
    current_params=current_params,
    performance_history=performance_history
)

print(f"Optimized parameters: {result.optimized_parameters}")
```

### 3. Setting Constraints

```python
# Define parameter constraints
constraints = {
    "max_cpc": {"min": 0.1, "max": 5.0},
    "daily_budget": {"min": 100.0, "max": 5000.0},
    "location_radius": {"min": 5.0, "max": 100.0},
    "target_cpa": {"min": 10.0, "max": 200.0}
}

# Apply constraints
optimizer.set_constraints(constraints)
```

## API Integration

### 1. Analytics Service Integration

The genetic algorithm is integrated into the existing `AnalyticsService`:

```python
from services.analytics_service import AnalyticsService

service = AnalyticsService()

# Configure genetic algorithm
config = {
    "population_size": 40,
    "max_generations": 75,
    "crossover_rate": 0.9,
    "mutation_rate": 0.05
}
await service.configure_genetic_algorithm(config)

# Use genetic optimization
result = await service.optimize_budget_allocation(
    campaigns=campaigns,
    total_budget=5000,
    objective="maximize_roi",
    optimization_method="genetic"  # Use "greedy" for traditional method
)
```

### 2. REST API Endpoints

#### Configure Genetic Algorithm
```http
POST /api/analytics/genetic/configure
Content-Type: application/json

{
    "population_size": 40,
    "max_generations": 75,
    "crossover_rate": 0.9,
    "mutation_rate": 0.05,
    "tournament_size": 3,
    "elitism_rate": 0.1
}
```

#### Budget Optimization
```http
POST /api/analytics/optimize/budget
Content-Type: application/json

{
    "campaigns": [...],
    "total_budget": 5000,
    "objective": "maximize_roi",
    "optimization_method": "genetic"
}
```

#### Parameter Optimization
```http
POST /api/analytics/optimize/parameters
Content-Type: application/json

{
    "current_params": {...},
    "performance_history": [...],
    "optimization_method": "genetic"
}
```

#### Set Constraints
```http
POST /api/analytics/constraints/set
Content-Type: application/json

{
    "constraints": {
        "max_cpc": {"min": 0.1, "max": 5.0},
        "daily_budget": {"min": 100.0, "max": 5000.0}
    }
}
```

#### Compare Methods
```http
POST /api/analytics/optimize/compare
Content-Type: application/json

{
    "campaigns": [...],
    "total_budget": 5000,
    "objective": "maximize_roi"
}
```

#### Get GA Status
```http
GET /api/analytics/genetic/status
```

## Performance Considerations

### 1. Population Size
- **Small (10-20)**: Faster execution, may miss optimal solutions
- **Medium (30-50)**: Good balance of speed and quality
- **Large (60-100)**: Better solutions, slower execution

### 2. Generation Limits
- **Budget Optimization**: 50-100 generations usually sufficient
- **Parameter Optimization**: 20-50 generations typically enough
- **Complex Problems**: May need 100+ generations

### 3. Early Termination
- **Stagnation**: Stops if no improvement for `max_stagnant_generations`
- **Convergence**: Stops if improvement falls below `convergence_threshold`
- **Manual**: Can be interrupted and resumed

### 4. Memory Usage
- **Population Size × Parameters**: Memory scales linearly
- **History Tracking**: Fitness history stored for monitoring
- **Cleanup**: Population is cleaned up after optimization

## Best Practices

### 1. Parameter Selection
- Start with default configuration
- Increase population size for complex problems
- Adjust mutation rate based on problem sensitivity
- Use constraints to guide search space

### 2. Objective Selection
- **maximize_roi**: Best for revenue optimization
- **maximize_conversions**: Best for lead generation
- **maximize_clicks**: Best for awareness campaigns
- **combined**: Balanced approach

### 3. Constraint Setting
- Set realistic bounds based on business rules
- Use tight constraints for sensitive parameters
- Allow wider bounds for exploratory optimization
- Monitor constraint violations

### 4. Performance Tuning
- Use smaller populations for quick experiments
- Increase generations for production optimization
- Enable early termination to save computation
- Monitor convergence patterns

## Comparison with Greedy Algorithm

| Aspect | Greedy Algorithm | Genetic Algorithm |
|--------|-----------------|-------------------|
| **Speed** | Fast (1 iteration) | Slower (multiple generations) |
| **Solution Quality** | Good for simple problems | Better for complex problems |
| **Global Optima** | May get trapped locally | Better global search |
| **Deterministic** | Yes | No (stochastic) |
| **Scalability** | Linear | Adjustable complexity |
| **Configuration** | Minimal | Highly configurable |
| **Use Case** | Quick optimization | Production optimization |

## Integration Testing

The implementation includes comprehensive test suites:

1. **Unit Tests**: Test individual components (chromosome, selection, crossover, mutation)
2. **Integration Tests**: Test service integration and API endpoints
3. **Performance Tests**: Verify optimization quality and convergence
4. **Validation Tests**: Ensure parameter validation and error handling

Run tests with:
```bash
cd backend
python -m pytest tests/test_genetic_optimizer.py -v
python -m pytest tests/test_genetic_analytics_integration.py -v
```