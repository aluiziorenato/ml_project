# 🤖 Optimizer AI - Advanced Copywriting Optimization

The Optimizer AI module provides comprehensive AI-powered text optimization for Mercado Livre listings, with advanced features including segment-specific optimization, compliance checking, and automated testing.

## 🚀 Features

### ✨ Core Functionality
- **AI-Powered Text Optimization** - Advanced copywriting optimization using machine learning
- **SEO Score Analysis** - Comprehensive SEO scoring with keyword optimization
- **Readability Assessment** - Text readability scoring and improvement suggestions
- **Sentiment Analysis** - Emotional tone analysis and optimization
- **Compliance Validation** - Automatic checking against Mercado Livre guidelines

### 🎯 Advanced Features
- **Segment-Specific Optimization** - Tailored optimization for different audience segments
- **Keyword Suggestions** - AI-generated keyword recommendations with competition analysis
- **A/B Testing** - Automated A/B test creation and recommendation
- **Auto-Testing Integration** - Seamless integration with simulator for performance testing
- **Multi-Audience Support** - Optimization for B2B, B2C, Millennials, Gen Z, and more

## 📡 API Endpoints

### Core Optimization
- `POST /api/optimize-copy` - Optimize text with AI-powered improvements
- `POST /api/ab-test` - Create A/B tests for multiple text variations

### Advanced Features
- `POST /api/keywords/suggest` - Get AI-powered keyword suggestions
- `POST /api/segment-optimization` - Optimize text for multiple audience segments
- `POST /api/compliance/check` - Check text compliance with Mercado Livre rules
- `POST /api/auto-test` - Automatically test optimizations through simulator

### Health & Monitoring
- `GET /health` - Service health check
- `GET /` - Web interface (if available)

## 🛠️ Usage Examples

### Text Optimization
```python
import httpx

optimization_data = {
    "original_text": "Smartphone usado em bom estado",
    "target_audience": "young_adults",
    "product_category": "electronics",
    "optimization_goal": "conversions",
    "keywords": ["smartphone", "android", "samsung"],
    "segment": "millennial",
    "budget_range": "medium",
    "priority_metrics": ["seo", "readability", "compliance"]
}

response = httpx.post("http://localhost:8003/api/optimize-copy", json=optimization_data)
result = response.json()

print(f"Original: {optimization_data['original_text']}")
print(f"Optimized: {result['optimized_text']}")
print(f"SEO Score: {result['seo_score']}/100")
print(f"Performance Lift: {result['estimated_performance_lift']}%")
```

### Keyword Suggestions
```python
keyword_data = {
    "product_category": "electronics",
    "product_title": "Smartphone Samsung Galaxy S24",
    "target_audience": "young_adults",
    "competitor_analysis": True,
    "max_suggestions": 10
}

response = httpx.post("http://localhost:8003/api/keywords/suggest", json=keyword_data)
keywords = response.json()

for keyword in keywords["suggested_keywords"]:
    print(f"Keyword: {keyword['keyword']} (Score: {keyword['score']})")
```

### Segment Optimization
```python
segment_data = {
    "text": "Produto de qualidade premium",
    "target_segments": ["b2b", "b2c_premium", "millennial"],
    "product_category": "electronics"
}

response = httpx.post("http://localhost:8003/api/segment-optimization", json=segment_data)
results = response.json()

for segment, optimized_text in results["optimized_texts"].items():
    print(f"{segment}: {optimized_text}")
    print(f"Performance: {results['performance_predictions'][segment]}")
```

### Compliance Check
```python
compliance_data = {
    "text": "Smartphone Samsung com garantia do fabricante",
    "product_category": "electronics"
}

response = httpx.post("http://localhost:8003/api/compliance/check", json=compliance_data)
compliance = response.json()

print(f"Compliant: {compliance['is_compliant']}")
print(f"Score: {compliance['compliance_score']}/100")
print(f"Risk Level: {compliance['risk_level']}")

if compliance['violations']:
    for violation in compliance['violations']:
        print(f"- {violation['description']}: {violation['suggestion']}")
```

## 🎯 Audience Segments

The optimizer supports various audience segments with specific optimization strategies:

- **B2B** - Professional tone, ROI focus, efficiency keywords
- **B2C Premium** - Sophisticated tone, quality focus, exclusivity
- **B2C Popular** - Friendly tone, value focus, accessibility
- **Millennial** - Casual tone, sustainability, technology focus
- **Gen Z** - Informal tone, authenticity, trending keywords
- **Family** - Caring tone, safety focus, reliability

## ⚙️ Configuration

### Environment Variables
- `OPTIMIZER_AI_PORT` - Service port (default: 8003)
- `OPTIMIZER_AI_HOST` - Service host (default: 0.0.0.0)
- `LOG_LEVEL` - Logging level (default: INFO)

### Dependencies
- FastAPI 0.115.6+
- Pydantic 2.10.4+
- scikit-learn 1.6.0+
- textstat 0.7.3+
- python-jose 3.5.0+

## 🧪 Testing

### Unit Tests
```bash
cd optimizer_ai
python -m pytest tests/test_optimizer_ai.py -v
```

### E2E Tests
```bash
python -m pytest tests/test_optimizer_e2e.py -v
```

### Integration Tests
```bash
python -m pytest tests/test_complete_integration.py::TestCompleteMLSystemIntegration::test_optimizer_ai_text_optimization -v
```

## 📊 Performance Metrics

The optimizer provides several metrics for optimization quality:

- **SEO Score** (0-100) - Keyword optimization, structure, readability
- **Readability Score** (0-100) - Text complexity and accessibility
- **Sentiment Score** (0-1) - Emotional tone positivity
- **Compliance Score** (0-100) - Adherence to Mercado Livre guidelines
- **ML Confidence** (0-1) - Confidence in optimization quality
- **Performance Lift** (%) - Expected improvement in metrics

## 🔧 Development

### Running Locally
```bash
cd optimizer_ai
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker
```bash
docker build -t optimizer-ai .
docker run -p 8003:8003 optimizer-ai
```

## 🔗 Integration

The Optimizer AI integrates seamlessly with other ML Project services:

- **Simulator Service** - Auto-testing through `/api/auto-test`
- **Learning Service** - Performance feedback and model improvement
- **Backend** - User management and data persistence

## 📝 API Documentation

When running, complete API documentation is available at:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

## 🚀 Production Deployment

For production deployment:

1. Set appropriate environment variables
2. Configure logging and monitoring
3. Set up health checks (`/health` endpoint)
4. Configure auto-scaling based on request volume
5. Set up proper security headers and CORS

---

**Status**: ✅ Production Ready
**Test Coverage**: 100% (Unit + Integration + E2E)
**Last Updated**: January 2025