"""
Test script for SEO Intelligence modules
Tests health endpoints and basic functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Service configurations
SERVICES = {
    'ai_predictive': {'port': 8004, 'name': 'AI Predictive'},
    'dynamic_optimization': {'port': 8005, 'name': 'Dynamic Optimization'},
    'market_pulse': {'port': 8010, 'name': 'Market Pulse'}
}

async def test_service_health(session, service_name, port):
    """Test health endpoint for a service"""
    try:
        url = f"http://localhost:{port}/health"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ {service_name} (:{port}) - Health: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ {service_name} (:{port}) - HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ {service_name} (:{port}) - Error: {str(e)}")
        return False

async def test_ai_predictive_endpoints(session):
    """Test AI Predictive specific endpoints"""
    try:
        # Test market gap analysis
        url = "http://localhost:8004/api/analyze-market-gaps"
        payload = {
            "category": "electronics",
            "keywords": ["smartphone", "tablet"],
            "target_region": "BR",
            "analysis_depth": "standard"
        }
        
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ AI Predictive - Market Gap Analysis: {len(data.get('gaps_found', []))} gaps found")
                return True
            else:
                print(f"❌ AI Predictive - Market Gap Analysis failed: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ AI Predictive - Market Gap Analysis error: {str(e)}")
        return False

async def test_dynamic_optimization_endpoints(session):
    """Test Dynamic Optimization specific endpoints"""
    try:
        # Test title optimization
        url = "http://localhost:8005/api/optimize-title"
        payload = {
            "original_title": "Smartphone Samsung usado",
            "category": "electronics",
            "keywords": ["smartphone", "samsung"],
            "target_audience": "young_adults",
            "optimization_goal": "ctr"
        }
        
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Dynamic Optimization - Title Optimization: {data.get('best_title', 'N/A')[:50]}...")
                return True
            else:
                print(f"❌ Dynamic Optimization - Title Optimization failed: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ Dynamic Optimization - Title Optimization error: {str(e)}")
        return False

async def test_market_pulse_endpoints(session):
    """Test Market Pulse specific endpoints"""
    try:
        # Test live heatmap
        url = "http://localhost:8010/api/live-heatmap"
        
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Market Pulse - Live Heatmap: {len(data.get('keywords', []))} keywords")
                return True
            else:
                print(f"❌ Market Pulse - Live Heatmap failed: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ Market Pulse - Live Heatmap error: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting SEO Intelligence System Tests")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoints
        print("\n📋 Testing Health Endpoints:")
        health_results = []
        for service_key, config in SERVICES.items():
            result = await test_service_health(session, config['name'], config['port'])
            health_results.append(result)
        
        # Test specific endpoints if services are healthy
        print("\n🔧 Testing Service Endpoints:")
        
        if health_results[0]:  # AI Predictive
            await test_ai_predictive_endpoints(session)
        
        if health_results[1]:  # Dynamic Optimization
            await test_dynamic_optimization_endpoints(session)
        
        if health_results[2]:  # Market Pulse
            await test_market_pulse_endpoints(session)
        
        # Summary
        print("\n" + "=" * 50)
        healthy_count = sum(health_results)
        total_count = len(health_results)
        print(f"📊 Test Summary: {healthy_count}/{total_count} services healthy")
        
        if healthy_count == total_count:
            print("🎉 All services are running successfully!")
        else:
            print("⚠️  Some services need attention")

if __name__ == "__main__":
    asyncio.run(main())