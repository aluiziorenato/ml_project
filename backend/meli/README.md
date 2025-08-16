# Mercado Libre Integration Services

## 🚀 Overview

This package provides a comprehensive, organized, and scalable integration with Mercado Libre APIs. It implements a modular architecture that avoids chaos and facilitates maintenance, expansion, and future integrations.

## 📁 Architecture

```
backend/meli/
├── __init__.py                    # Main package initialization
├── interfaces.py                  # Standard interfaces and contracts
├── base.py                       # Base service class with common functionality
├── orders_service/               # Order management and analytics
│   ├── __init__.py
│   └── README.md
├── shipments_service/            # Shipping and logistics management  
│   ├── __init__.py
│   └── README.md
├── messages_service/             # Messaging with AI-powered responses
│   ├── __init__.py
│   └── README.md
├── questions_service/            # Q&A management with automated answers
│   ├── __init__.py
│   └── README.md
├── inventory_service/            # Stock control and demand prediction
│   ├── __init__.py
│   └── README.md
└── reputation_service/           # Reputation monitoring and analytics
    ├── __init__.py
    └── README.md
```

## 🎯 Design Principles

### 🔧 Standardized Architecture
- **Consistent interfaces** across all services
- **Common base class** with shared functionality
- **Standardized error handling** and logging
- **Unified response formats**

### 🔗 Service Integration
- **Analytics Service** - Automatic event tracking and metrics
- **Optimizer AI** - Smart suggestions and optimizations  
- **Learning Service** - ML insights and predictive analytics
- **Campaign Automation** - Seamless workflow integration

### 📊 Data-Driven Insights
- **Real-time analytics** for all services
- **Machine learning** predictions and recommendations
- **Performance monitoring** and optimization
- **Competitive intelligence**

## 🛠️ Core Services

### 📦 Orders Service
Complete order management with analytics and ML integration.

**Key Features:**
- Order listing with advanced filters
- Status tracking and updates
- Revenue analytics and reporting
- Sales prediction and optimization

**Endpoints:**
- `GET /meli/orders_service/orders` - List orders
- `GET /meli/orders_service/orders/{id}` - Order details
- `GET /meli/orders_service/analytics` - Sales analytics

### 🚚 Shipments Service  
Comprehensive shipping and logistics management.

**Key Features:**
- Shipment tracking and status updates
- Shipping cost optimization
- Delivery analytics
- Label generation and management

**Endpoints:**
- `GET /meli/shipments_service/shipments` - List shipments
- `GET /meli/shipments_service/shipments/{id}/tracking` - Tracking info
- `GET /meli/shipments_service/shipping_options` - Available options

### 💬 Messages Service
Intelligent messaging with AI-powered responses.

**Key Features:**
- Message management and organization
- AI-generated response suggestions
- Sentiment analysis and urgency detection
- Communication analytics

**Endpoints:**
- `GET /meli/messages_service/messages` - List messages
- `GET /meli/messages_service/ai_suggestions` - AI response suggestions
- `POST /meli/messages_service/messages` - Send message

### ❓ Questions Service
Q&A management with automated answers and knowledge base.

**Key Features:**
- Question prioritization and organization
- AI-powered answer generation
- Knowledge base integration
- Response analytics and optimization

**Endpoints:**
- `GET /meli/questions_service/questions` - List questions
- `POST /meli/questions_service/answers` - Answer question
- `GET /meli/questions_service/ai_suggestions` - AI answer suggestions

### 📦 Inventory Service
Smart inventory management with demand prediction.

**Key Features:**
- Real-time stock monitoring
- Demand forecasting with ML
- Automated restock alerts
- Inventory optimization

**Endpoints:**
- `GET /meli/inventory_service/inventory` - List inventory
- `GET /meli/inventory_service/alerts` - Stock alerts
- `PUT /meli/inventory_service/items/{id}/stock` - Update stock

### ⭐ Reputation Service
Reputation monitoring and optimization system.

**Key Features:**
- Real-time reputation tracking
- Review sentiment analysis
- Improvement suggestions
- Competitive benchmarking

**Endpoints:**
- `GET /meli/reputation_service/reputation/{user_id}` - Reputation data
- `GET /meli/reputation_service/analytics` - Reputation analytics
- `GET /meli/reputation_service/reviews` - Review analysis

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install httpx fastapi uvicorn

# Import services
from meli.orders_service import orders_service
from meli.messages_service import messages_service
from meli.questions_service import questions_service
```

### Basic Usage

```python
import asyncio
from meli.orders_service import orders_service

async def main():
    # Health check
    health = await orders_service.health_check()
    print(f"Service status: {health.data['status']}")
    
    # Get orders (with valid access token)
    orders = await orders_service.list_items(
        access_token="your_token",
        user_id="your_user_id",
        limit=10
    )
    
    if orders.success:
        print(f"Found {len(orders.data)} orders")

asyncio.run(main())
```

### FastAPI Integration

```python
from fastapi import FastAPI
from backend.app.routers.meli_services_router import router

app = FastAPI()
app.include_router(router, prefix="/meli", tags=["Mercado Livre Services"])
```

## 📊 Analytics & AI Integration

### Analytics Service Integration
All services automatically send events to the analytics service:

```python
# Automatic event tracking
await self._send_analytics_event("orders_listed", {
    "user_id": user_id,
    "total_orders": len(orders),
    "filters": filters
})
```

### Optimizer AI Integration
Services get optimization suggestions:

```python
# Get AI optimization suggestions
suggestions = await self._get_optimizer_suggestions({
    "service": "orders",
    "context": order_data
})
```

### Learning Service Integration
Machine learning insights and predictions:

```python
# Get learning insights
insights = await self._get_learning_insights({
    "task": "demand_forecast",
    "data": historical_data
})
```

## 🔧 Configuration

### Environment Variables

```bash
# Service URLs
ANALYTICS_SERVICE_URL=http://localhost:8002
OPTIMIZER_AI_URL=http://localhost:8003
LEARNING_SERVICE_URL=http://localhost:8004
CAMPAIGN_AUTOMATION_URL=http://localhost:8005

# Mercado Libre API
ML_API_URL=https://api.mercadolibre.com
ML_CLIENT_ID=your_client_id
ML_CLIENT_SECRET=your_client_secret

# Service Configuration
SERVICE_TIMEOUT=30
CACHE_TTL=3600
LOG_LEVEL=INFO
```

### Service Configuration

```python
from meli.base import BaseMeliService

class CustomService(BaseMeliService):
    def __init__(self):
        super().__init__("custom_service")
        
        # Custom configuration
        self.timeout = 45
        self.max_retries = 3
        self.cache_enabled = True
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
cd backend
python -m pytest tests/meli/ -v

# Run specific service tests
python -m pytest tests/meli/test_meli_services.py::TestMeliServices::test_orders_service_health -v
```

### Test Structure

```python
import pytest
from meli.orders_service import orders_service

@pytest.mark.asyncio
async def test_orders_service_health():
    result = await orders_service.health_check()
    assert result.success is True
    assert result.data["service"] == "orders_service"
```

## 🎨 Frontend Integration

### React Components

Pre-built React components for easy frontend integration:

```jsx
import MessagesManager from './components/Meli/MessagesManager';
import QuestionsManager from './components/Meli/QuestionsManager';
import AnalyticsDashboard from './components/Meli/AnalyticsDashboard';

function MeliDashboard({ userId, accessToken }) {
  return (
    <div>
      <AnalyticsDashboard userId={userId} accessToken={accessToken} />
      <MessagesManager userId={userId} accessToken={accessToken} />
      <QuestionsManager userId={userId} accessToken={accessToken} />
    </div>
  );
}
```

### API Endpoints

All endpoints are configured in `frontend/src/api/endpoints.ts`:

```typescript
export const endpoints = {
  meli: {
    orders: {
      list: '/meli/orders_service/orders',
      analytics: '/meli/orders_service/analytics'
    },
    messages: {
      list: '/meli/messages_service/messages',
      aiSuggestions: '/meli/messages_service/ai_suggestions'
    }
    // ... more endpoints
  }
};
```

## 📈 Monitoring & Observability

### Health Checks

```bash
# Check all services status
curl http://localhost:8000/meli/status

# Check individual service
curl http://localhost:8000/meli/orders_service/health
```

### Metrics & Logging

```python
import logging

# Service-specific logger
logger = logging.getLogger("meli.orders_service")

# Automatic metrics collection
await self._send_analytics_event("metric_name", {
    "value": metric_value,
    "timestamp": datetime.utcnow().isoformat()
})
```

### Performance Monitoring

- **Response times** for all endpoints
- **Success rates** and error tracking
- **ML model performance** metrics
- **Business KPIs** tracking

## 🔐 Security & Best Practices

### Authentication
- **Token-based** authentication with ML API
- **Automatic token refresh** handling
- **Secure token storage**

### Error Handling
- **Standardized error responses**
- **Graceful degradation**
- **Retry mechanisms** with exponential backoff

### Rate Limiting
- **Intelligent rate limiting** respecting ML API limits
- **Request queuing** for high-volume operations
- **Circuit breaker** pattern implementation

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  meli-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ML_CLIENT_ID=${ML_CLIENT_ID}
      - ML_CLIENT_SECRET=${ML_CLIENT_SECRET}
      - ANALYTICS_SERVICE_URL=http://analytics:8002
```

### Production Considerations

- **Load balancing** for high availability
- **Database clustering** for scalability
- **Redis caching** for performance
- **Monitoring** and alerting setup

## 🔄 Migration from Legacy

### Step-by-Step Migration

1. **Install new package** alongside existing code
2. **Run health checks** to verify connectivity
3. **Migrate service by service** starting with orders
4. **Update frontend** to use new endpoints
5. **Monitor performance** and rollback if needed

### Backward Compatibility

The new structure maintains compatibility with existing endpoints:

```python
# Old endpoint still works
app.include_router(meli_routes.router, prefix="/meli", tags=["Mercado Livre"])

# New organized endpoints
app.include_router(meli_services_router.router, prefix="/meli", tags=["Mercado Livre Services"])
```

## 📚 Documentation

Each service includes comprehensive documentation:

- **API Reference** with examples
- **Integration guides** 
- **Troubleshooting** tips
- **Best practices**

### Service Documentation
- [Orders Service README](./orders_service/README.md)
- [Shipments Service README](./shipments_service/README.md)
- [Messages Service README](./messages_service/README.md)
- [Questions Service README](./questions_service/README.md)
- [Inventory Service README](./inventory_service/README.md)
- [Reputation Service README](./reputation_service/README.md)

## 🛣️ Roadmap

### Phase 1 (Completed) ✅
- [x] Core service architecture
- [x] Basic CRUD operations
- [x] Health checks and monitoring
- [x] Frontend components
- [x] Documentation

### Phase 2 (Next)
- [ ] Advanced AI features
- [ ] Real-time notifications
- [ ] Batch operations
- [ ] Enhanced caching
- [ ] Performance optimizations

### Phase 3 (Future)
- [ ] Multi-marketplace support
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Webhook management
- [ ] A/B testing framework

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/aluiziorenato/ml_project.git
cd ml_project/backend

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest tests/meli/ -v

# Start development server
uvicorn app.main:app --reload
```

### Code Standards

- **PEP 8** compliance
- **Type hints** for all functions
- **Comprehensive tests** for new features
- **Documentation** for all public APIs

### Submitting Changes

1. Fork the repository
2. Create feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📞 Support

### Getting Help

- **Documentation**: Check service-specific READMEs
- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions

### Common Issues

**Service not responding**
```bash
# Check service health
curl http://localhost:8000/meli/orders_service/health
```

**Authentication errors**
```bash
# Verify token configuration
echo $ML_CLIENT_ID
echo $ML_CLIENT_SECRET
```

**Import errors**
```python
# Verify package installation
import sys
sys.path.append('.')
from meli.orders_service import orders_service
```

## 📄 License

MIT License - see [LICENSE](../../../LICENSE) file for details.

---

**Built with ❤️ for seamless Mercado Libre integration**