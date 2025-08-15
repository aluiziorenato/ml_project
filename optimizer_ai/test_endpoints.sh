#!/bin/bash

# Test script for Optimizer AI service
# Tests all endpoints with various scenarios

set -e

BASE_URL="http://localhost:8001"

echo "🧪 Testing Optimizer AI Service..."
echo "=================================="

# Function to test endpoint
test_endpoint() {
    local endpoint="$1"
    local data="$2"
    local description="$3"
    
    echo "Testing: $description"
    echo "Endpoint: $endpoint"
    echo "Data: $data"
    
    response=$(curl -s -X POST "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    if [ $? -eq 0 ]; then
        echo "✅ Success"
        echo "Response: $response" | python -m json.tool
    else
        echo "❌ Failed"
        echo "Response: $response"
    fi
    echo "---"
}

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$BASE_URL/health" | python -m json.tool
echo "---"

# Test root endpoint
echo "Testing root endpoint..."
curl -s "$BASE_URL/" | python -m json.tool
echo "---"

# Test generate_title endpoint - basic
test_endpoint "/generate_title" \
    '{"text": "Smartphone inovador com IA"}' \
    "Title generation - basic"

# Test generate_title endpoint - with keywords and tone
test_endpoint "/generate_title" \
    '{"text": "Tênis esportivo de alta performance", "keywords": ["tênis", "performance"], "tone": "exciting", "max_length": 40}' \
    "Title generation - with keywords and exciting tone"

# Test generate_title endpoint - luxury tone
test_endpoint "/generate_title" \
    '{"text": "Relógio suíço de luxo", "tone": "luxury", "max_length": 50}' \
    "Title generation - luxury tone"

# Test generate_description endpoint - basic
test_endpoint "/generate_description" \
    '{"text": "Software de gestão empresarial"}' \
    "Description generation - basic"

# Test generate_description endpoint - full parameters
test_endpoint "/generate_description" \
    '{"text": "Plataforma de e-commerce completa", "keywords": ["e-commerce", "vendas"], "tone": "professional", "max_length": 200, "cta_style": "direct"}' \
    "Description generation - full parameters"

# Test generate_description endpoint - casual tone with soft CTA
test_endpoint "/generate_description" \
    '{"text": "App de fitness e saúde", "tone": "casual", "max_length": 150, "cta_style": "soft"}' \
    "Description generation - casual tone with soft CTA"

echo "🎉 All tests completed!"