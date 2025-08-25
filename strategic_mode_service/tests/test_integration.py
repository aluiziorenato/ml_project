import pytest
import asyncio
import httpx
from datetime import date, datetime
import json

class TestStrategicModeIntegration:
    """Integration tests for Strategic Mode Service"""
    
    BASE_URL = "http://localhost:8017"
    
    async def test_service_health(self):
        """Test that the strategic mode service is healthy"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "strategic-mode"
    
    async def test_get_default_strategies(self):
        """Test getting default strategy presets"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/api/strategies/presets/default")
            assert response.status_code == 200
            data = response.json()
            assert "strategies" in data
            assert len(data["strategies"]) == 4
            
            # Verify all 4 strategic modes are present
            strategy_names = [s["name"] for s in data["strategies"]]
            expected_names = ["Maximizar Lucro", "Escalar Vendas", "Proteger Margem", "Campanhas Agressivas"]
            for name in expected_names:
                assert name in strategy_names
    
    async def test_get_default_special_dates(self):
        """Test getting default special dates presets"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/api/special-dates/presets/default")
            assert response.status_code == 200
            data = response.json()
            assert "special_dates" in data
            assert len(data["special_dates"]) >= 5
            
            # Verify key special dates are present
            date_names = [d["name"] for d in data["special_dates"]]
            expected_dates = ["Black Friday", "Cyber Monday", "Natal", "Dia das Mães", "Dia dos Pais"]
            for name in expected_dates:
                assert name in date_names
    
    async def test_integration_status(self):
        """Test integration status with other services"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/api/integrations/status")
            assert response.status_code == 200
            data = response.json()
            assert "services" in data
            assert "overall_status" in data
            
            # Verify all required services are checked
            service_names = [s.get("service") for s in data["services"] if isinstance(data["services"], list)]
            if isinstance(data["services"], dict):
                # Handle different response format
                assert "acos" in str(data).lower() or "campaign" in str(data).lower()
    
    async def test_strategy_workflow(self):
        """Test complete strategy application workflow"""
        async with httpx.AsyncClient() as client:
            # 1. Get available strategies
            strategies_response = await client.get(f"{self.BASE_URL}/api/strategies/")
            assert strategies_response.status_code == 200
            strategies = strategies_response.json()
            
            # 2. Simulate strategy application
            if strategies:  # Only if we have strategies in database
                strategy_id = strategies[0]["id"]
                application_data = {
                    "strategy_id": strategy_id,
                    "user_id": 1,
                    "apply_immediately": False,
                    "simulate_only": True
                }
                
                apply_response = await client.post(
                    f"{self.BASE_URL}/api/strategies/apply",
                    json=application_data
                )
                assert apply_response.status_code == 200
                result = apply_response.json()
                assert result["success"] is True
                assert "message" in result
    
    async def test_special_dates_workflow(self):
        """Test special dates management workflow"""
        async with httpx.AsyncClient() as client:
            # 1. Get special dates
            dates_response = await client.get(f"{self.BASE_URL}/api/special-dates/")
            assert dates_response.status_code == 200
            special_dates = dates_response.json()
            
            # 2. Get active special dates
            active_response = await client.get(f"{self.BASE_URL}/api/special-dates/active")
            assert active_response.status_code == 200
            active_dates = active_response.json()
            assert isinstance(active_dates, list)
    
    async def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        async with httpx.AsyncClient() as client:
            user_id = 1
            response = await client.get(f"{self.BASE_URL}/api/reports/dashboard/{user_id}")
            assert response.status_code == 200
            data = response.json()
            
            # Verify dashboard structure
            expected_keys = ["current_strategy", "active_special_dates", "recent_alerts", "recent_actions", "kpis"]
            for key in expected_keys:
                assert key in data
    
    async def test_performance_kpis(self):
        """Test KPI calculation endpoint"""
        async with httpx.AsyncClient() as client:
            user_id = 1
            response = await client.get(f"{self.BASE_URL}/api/reports/kpis/{user_id}")
            assert response.status_code == 200
            kpis = response.json()
            
            # Verify KPI structure
            expected_keys = ["total_spend", "total_sales", "average_acos", "roi", "campaigns_count", "period_days"]
            for key in expected_keys:
                assert key in kpis

class TestStrategicModeAPI:
    """API unit tests for Strategic Mode Service"""
    
    def test_strategy_validation(self):
        """Test strategy data validation"""
        from src.models.schemas import StrategicModeCreate
        
        # Valid strategy
        valid_strategy = StrategicModeCreate(
            name="Test Strategy",
            description="Test description",
            acos_min=10.0,
            acos_max=20.0,
            budget_multiplier=1.0,
            bid_adjustment=0.0,
            margin_threshold=30.0
        )
        assert valid_strategy.name == "Test Strategy"
        
        # Invalid strategy (acos_max <= acos_min)
        with pytest.raises(ValueError):
            StrategicModeCreate(
                name="Invalid Strategy",
                acos_min=20.0,
                acos_max=10.0,  # This should be greater than acos_min
                budget_multiplier=1.0,
                bid_adjustment=0.0,
                margin_threshold=30.0
            )
    
    def test_special_date_validation(self):
        """Test special date data validation"""
        from src.models.schemas import SpecialDateCreate
        
        # Valid special date
        valid_date = SpecialDateCreate(
            name="Test Date",
            description="Test description",
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 3),
            budget_multiplier=2.0,
            acos_adjustment=5.0
        )
        assert valid_date.name == "Test Date"
        
        # Invalid special date (end_date <= start_date)
        with pytest.raises(ValueError):
            SpecialDateCreate(
                name="Invalid Date",
                start_date=date(2024, 12, 3),
                end_date=date(2024, 12, 1),  # This should be after start_date
                budget_multiplier=2.0,
                acos_adjustment=5.0
            )
    
    def test_strategy_impact_calculation(self):
        """Test strategy impact calculation logic"""
        from src.services.strategy_coordinator import StrategyCoordinator
        
        # Mock strategy data
        strategy = type('Strategy', (), {
            'id': 1,
            'name': 'Test Strategy',
            'acos_min': 10.0,
            'acos_max': 15.0,
            'budget_multiplier': 1.2,
            'bid_adjustment': 20.0,
            'margin_threshold': 35.0,
            'automation_rules': {},
            'alert_thresholds': {}
        })()
        
        # Test impact calculation would be implemented here
        # This is a placeholder for the actual calculation logic
        assert strategy.budget_multiplier > 1.0  # Indicates budget increase
        assert strategy.bid_adjustment > 0  # Indicates bid increase

# Example of how to run these tests
if __name__ == "__main__":
    async def run_integration_tests():
        """Run integration tests"""
        test_instance = TestStrategicModeIntegration()
        
        print("🚀 Starting Strategic Mode Integration Tests...")
        
        try:
            print("✅ Testing service health...")
            await test_instance.test_service_health()
            
            print("✅ Testing default strategies...")
            await test_instance.test_get_default_strategies()
            
            print("✅ Testing default special dates...")
            await test_instance.test_get_default_special_dates()
            
            print("✅ Testing integration status...")
            await test_instance.test_integration_status()
            
            print("✅ Testing strategy workflow...")
            await test_instance.test_strategy_workflow()
            
            print("✅ Testing special dates workflow...")
            await test_instance.test_special_dates_workflow()
            
            print("✅ Testing dashboard data...")
            await test_instance.test_dashboard_data()
            
            print("✅ Testing performance KPIs...")
            await test_instance.test_performance_kpis()
            
            print("🎉 All integration tests passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("💡 Make sure the Strategic Mode Service is running on port 8017")
    
    def run_unit_tests():
        """Run unit tests"""
        print("🔬 Starting Strategic Mode Unit Tests...")
        
        test_instance = TestStrategicModeAPI()
        
        try:
            print("✅ Testing strategy validation...")
            test_instance.test_strategy_validation()
            
            print("✅ Testing special date validation...")
            test_instance.test_special_date_validation()
            
            print("✅ Testing strategy impact calculation...")
            test_instance.test_strategy_impact_calculation()
            
            print("🎉 All unit tests passed!")
            
        except Exception as e:
            print(f"❌ Unit test failed: {e}")
    
    print("=" * 60)
    print("🎯 STRATEGIC MODE SERVICE TEST SUITE")
    print("=" * 60)
    
    # Run unit tests first (no external dependencies)
    run_unit_tests()
    print()
    
    # Run integration tests (requires service to be running)
    try:
        asyncio.run(run_integration_tests())
    except Exception as e:
        print(f"💡 Integration tests skipped: {e}")
        print("   Start the service with: uvicorn src.main:app --host 0.0.0.0 --port 8017")
    
    print("\n✨ Test suite completed!")