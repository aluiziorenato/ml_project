# 🚀 ML Automation System - Complete Implementation

This project implements a comprehensive ML automation system for Mercado Libre with three independent microservices, complete authentication, monitoring, and CI/CD pipeline.

## 📦 Services Overview

### 🎯 Simulator Service (Port 8001)
Campaign simulation and management service
- **Complete CRUD API** for campaigns
- **Campaign analytics** and statistics
- **Advanced simulation algorithms** with category/audience multipliers
- **11 comprehensive unit tests** with 95%+ coverage

**Key Endpoints:**
- `POST /api/simulate` - Create campaign simulation
- `GET /api/campaigns` - List campaigns (with pagination/filtering)
- `GET /api/simulation/{id}` - Get campaign details
- `PUT /api/simulation/{id}` - Update campaign
- `DELETE /api/simulation/{id}` - Delete campaign
- `GET /api/campaigns/stats` - Campaign statistics

### 🧠 Learning Service (Port 8002)
ML model management and training service
- **Complete model lifecycle management** (CRUD)
- **Training job management** (start, monitor, cancel)
- **Model predictions** with multiple algorithm support
- **Model performance analytics**
- **16 comprehensive unit tests** with 90%+ coverage

**Key Endpoints:**
- `POST /api/models` - Create ML model
- `GET /api/models` - List models (with filtering)
- `POST /api/models/{id}/train` - Start training job
- `GET /api/training-jobs/{id}` - Monitor training progress
- `POST /api/models/{id}/predict` - Make predictions
- `GET /api/stats/models` - Model statistics

### ✨ Optimizer AI Service (Port 8003)
Copywriting optimization and A/B testing service
- **Advanced copywriting optimization** with AI techniques
- **Complete A/B test management** lifecycle
- **Template management system** for reusable copy
- **Batch optimization** for multiple texts
- **Statistical analysis** with confidence levels
- **21 comprehensive unit tests** with 92%+ coverage

**Key Endpoints:**
- `POST /api/optimize-copy` - Optimize copywriting
- `POST /api/ab-test` - Create A/B test
- `POST /api/ab-tests/{id}/start` - Start A/B test
- `GET /api/ab-tests/{id}/results` - Get test results
- `POST /api/templates` - Create copy template
- `POST /api/optimize-batch` - Batch optimization

## 🔐 Authentication & Security

**JWT-based authentication** implemented across all services:

### Authentication Endpoints
- `POST /api/auth/token` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh JWT token

### User Roles & Scopes
- **Admin**: Full access (`admin`, `read`, `write`)
- **User**: Standard access (`read`, `write`)
- **ReadOnly**: View-only access (`read`)

### Protected Endpoints
All CRUD operations require appropriate scopes:
- `read` scope: GET operations
- `write` scope: POST, PUT, DELETE operations
- `admin` scope: Administrative functions

**Example Login:**
```bash
curl -X POST http://localhost:8001/api/auth/token \
  -F "username=admin" \
  -F "password=admin"
```

## 📊 Monitoring & Observability

**Complete Prometheus/Grafana monitoring stack:**

### Metrics Collected
- **HTTP request metrics** (rate, duration, status codes)
- **Business metrics** (campaigns, models, A/B tests)
- **Service health** and availability
- **Resource utilization**

### Grafana Dashboard
Access at: `http://localhost:3001` (admin/admin123)
- Real-time service metrics
- Business KPIs dashboard
- Error rate monitoring
- Performance analytics

### Alerting Rules
- Service downtime alerts
- High error rate warnings
- Performance degradation alerts
- Business metric anomalies

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Simulator      │    │   Learning      │    │  Optimizer AI   │
│  Service        │    │   Service       │    │   Service       │
│  (Port 8001)    │    │  (Port 8002)    │    │  (Port 8003)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Backend       │
                    │   (Port 8000)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Database      │
                    └─────────────────┘

         ┌─────────────────┐    ┌─────────────────┐
         │   Prometheus    │    │    Grafana      │
         │   (Port 9090)   │    │   (Port 3001)   │
         └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ml_project
```

### 2. Start All Services
```bash
# Production environment with monitoring
docker-compose -f docker-compose.prod.yml up -d

# Development environment
docker-compose up -d
```

### 3. Verify Services
```bash
# Check service health
curl http://localhost:8001/health  # Simulator
curl http://localhost:8002/health  # Learning
curl http://localhost:8003/health  # Optimizer

# Access Swagger documentation
open http://localhost:8001/docs  # Simulator API docs
open http://localhost:8002/docs  # Learning API docs
open http://localhost:8003/docs  # Optimizer API docs
```

### 4. Get Authentication Token
```bash
# Login as admin user
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/token \
  -F "username=admin" \
  -F "password=admin" | jq -r '.access_token')

echo "Bearer $TOKEN"
```

### 5. Test APIs with Authentication
```bash
# Create a campaign simulation
curl -X POST http://localhost:8001/api/simulate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 15 Pro",
    "category": "electronics",
    "budget": 1000.0,
    "duration_days": 30,
    "target_audience": "young_adults",
    "keywords": ["iphone", "smartphone", "apple"]
  }'
```

## 🧪 Testing

### Run All Tests
```bash
# Simulator service tests
cd simulator_service
pytest tests/ -v --cov=app

# Learning service tests  
cd learning_service
pytest tests/ -v --cov=app

# Optimizer AI tests
cd optimizer_ai
pytest tests/ -v --cov=app
```

### Test Coverage
- **Simulator Service**: 11 tests, 95%+ coverage
- **Learning Service**: 16 tests, 90%+ coverage
- **Optimizer AI**: 21 tests, 92%+ coverage
- **Total**: 48 comprehensive business logic tests

## 🔄 CI/CD Pipeline

**GitHub Actions workflow** with comprehensive testing:

### Pipeline Stages
1. **Unit Tests** - All services tested in parallel
2. **Security Scanning** - Trivy vulnerability scanning
3. **Docker Builds** - Multi-platform builds for all services
4. **Integration Tests** - End-to-end service testing
5. **E2E Tests** - Frontend user journey testing
6. **Deployment** - Automated production deployment

### Quality Gates
- ✅ All tests must pass
- ✅ Security scan must pass
- ✅ Docker builds must succeed
- ✅ Code coverage > 85%

## 📝 API Documentation

### Swagger/OpenAPI
Each service provides interactive API documentation:
- **Simulator**: http://localhost:8001/docs
- **Learning**: http://localhost:8002/docs
- **Optimizer**: http://localhost:8003/docs

### Authentication Required
Most endpoints require JWT authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

## 🐳 Docker & Kubernetes

### Docker Images
Each service has optimized multi-stage Dockerfiles:
```bash
# Build individual services
docker build -t simulator-service ./simulator_service
docker build -t learning-service ./learning_service
docker build -t optimizer-ai ./optimizer_ai
```

### Kubernetes Deployment
```bash
# Deploy all services to Kubernetes
kubectl apply -f simulator_service/k8s/
kubectl apply -f learning_service/k8s/
kubectl apply -f optimizer_ai/k8s/

# Check deployment status
kubectl get pods -l component=ml-automation
```

## 📈 Monitoring Access

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Metrics endpoint**: http://localhost:800X/metrics (for each service)

### Grafana Dashboards
- **URL**: http://localhost:3001
- **Login**: admin / admin123
- **Dashboard**: ML Automation Services

### Key Metrics
- HTTP request rate and latency
- Error rates by service
- Campaign creation rate
- Model training status
- A/B test performance
- Resource utilization

## 🛠️ Development

### Local Development Setup
```bash
# Install dependencies for each service
cd simulator_service && pip install -r requirements.txt
cd learning_service && pip install -r requirements.txt  
cd optimizer_ai && pip install -r requirements.txt

# Run services locally
python simulator_service/app/main.py  # Port 8001
python learning_service/app/main.py   # Port 8002
python optimizer_ai/app/main.py       # Port 8003
```

### Adding New Features
1. **Create feature branch**
2. **Add tests first** (TDD approach)
3. **Implement functionality**
4. **Update API documentation**
5. **Add metrics if needed**
6. **Test authentication/authorization**
7. **Submit PR with tests**

## 🔒 Security Features

- **JWT Authentication** with role-based access control
- **CORS configuration** for cross-origin requests
- **Input validation** with Pydantic models
- **SQL injection protection** with parameterized queries
- **Rate limiting** (recommended for production)
- **HTTPS support** (configure in nginx)

## 📊 Business Metrics

### Campaign Analytics
- Total campaigns created
- Active vs inactive campaigns
- Success rates by category
- ROI analysis

### Model Performance
- Training job success rates
- Model accuracy metrics
- Prediction volume
- Model usage patterns

### A/B Testing
- Test completion rates
- Statistical significance
- Conversion improvements
- Template usage

## 🚀 Production Deployment

### Environment Variables
Set these in production:
```bash
# JWT Security
SECRET_KEY=your-production-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

### Scaling Considerations
- **Horizontal scaling**: Multiple instances per service
- **Load balancing**: Nginx or cloud load balancer
- **Database**: PostgreSQL with read replicas
- **Monitoring**: Centralized logging with ELK stack
- **Security**: WAF, rate limiting, API keys

## 🎯 Next Steps

- [ ] Add Redis caching layer
- [ ] Implement rate limiting
- [ ] Add email notifications
- [ ] Create mobile app interface
- [ ] Add machine learning model versioning
- [ ] Implement advanced analytics
- [ ] Add multi-tenant support

## 📞 Support

For questions or issues:
- Check the API documentation at `/docs` endpoints
- Review test cases for usage examples
- Monitor Grafana dashboards for service health
- Check Prometheus metrics for detailed monitoring

---

**Built for Mercado Libre** 🇧🇷  
Production-ready ML automation system with comprehensive testing, monitoring, and documentation.