# 🚀 Campaign Automation Service

Advanced campaign automation system for Mercado Livre with AI-powered optimization.

## 🎯 Overview

The Campaign Automation Service is a containerized microservice that provides comprehensive campaign management, AI-powered optimization, performance analytics, and competitor monitoring capabilities. It integrates seamlessly with existing ML services to provide a complete automation solution.

## 🏗️ Architecture

```
campaign_automation_service/
├── Dockerfile                    # Multi-stage Docker build
├── requirements.txt             # Python dependencies
├── src/
│   ├── api/
│   │   └── routes.py           # FastAPI routes and endpoints
│   ├── core/
│   │   ├── campaign_manager.py # Campaign CRUD operations
│   │   ├── metrics_analyzer.py # Performance analytics
│   │   └── competitor_monitor.py # Competitor intelligence
│   ├── models/
│   │   └── campaign_models.py  # Pydantic and SQLAlchemy models
│   ├── services/
│   │   ├── ai_integration.py   # AI service integrations
│   │   └── scheduler.py        # Task scheduling system
│   ├── utils/
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Structured logging
│   └── main.py                # FastAPI application
└── tests/
    └── test_campaign_automation.py # Comprehensive tests
```

## ✨ Key Features

### 📊 Campaign Management
- Complete CRUD operations for advertising campaigns
- Campaign lifecycle management (draft → active → paused → completed)
- Budget and bidding strategy management
- Target audience and keyword management

### 🤖 AI-Powered Optimization
- **Copy Optimization**: Automated ad copy enhancement using AI
- **Performance Prediction**: ML-based campaign performance forecasting
- **Bidding Optimization**: Smart bid adjustments based on performance data
- **A/B Testing**: Automated test creation and statistical analysis

### 📈 Performance Analytics
- Real-time metrics tracking (CTR, CPC, ROAS, ROI)
- Hourly and daily performance breakdowns
- Trend analysis and performance insights
- Benchmark comparisons against industry standards

### 🕵️ Competitor Intelligence
- Automated competitor monitoring
- Keyword competition analysis
- Pricing intelligence gathering
- Market share analysis
- Threat assessment and opportunity identification

### ⚡ Task Automation
- Scheduled optimization tasks
- Automated performance monitoring
- Budget adjustment automation
- Report generation scheduling
- Celery-based asynchronous processing

## 🔧 Technical Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for caching and session storage
- **Queue**: Celery for asynchronous task processing
- **Authentication**: JWT tokens with rate limiting
- **Monitoring**: Structured logging with health checks
- **Containerization**: Docker with multi-stage builds

## 🌐 Service Integration

The service integrates with existing ML ecosystem:

- **Simulator Service (8001)**: Campaign performance simulation
- **Learning Service (8002)**: Machine learning insights
- **Optimizer AI (8003)**: Copy optimization and enhancement
- **PostgreSQL**: Shared data persistence
- **Redis**: Distributed caching and task queues

## 🚀 Quick Start

### Using Docker Compose

```bash
# Start all services including campaign automation
docker-compose up campaign_automation_service

# Or start entire ecosystem
docker-compose up
```

### Direct Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/nome_do_banco"
export REDIS_URL="redis://localhost:6379/14"
export SIMULATOR_SERVICE_URL="http://localhost:8001"
export OPTIMIZER_AI_URL="http://localhost:8003"
export LEARNING_SERVICE_URL="http://localhost:8002"

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8014 --reload
```

## 📋 API Endpoints

### Campaign Management
- `POST /api/campaigns` - Create new campaign
- `GET /api/campaigns` - List campaigns with filters
- `GET /api/campaigns/{id}` - Get campaign details
- `PUT /api/campaigns/{id}` - Update campaign
- `POST /api/campaigns/{id}/activate` - Activate campaign
- `POST /api/campaigns/{id}/pause` - Pause campaign

### Analytics & Metrics
- `GET /api/campaigns/{id}/metrics` - Get performance summary
- `GET /api/campaigns/{id}/metrics/hourly` - Hourly breakdown
- `GET /api/campaigns/{id}/metrics/daily` - Daily aggregation
- `GET /api/campaigns/{id}/analysis/trends` - Trend analysis
- `GET /api/campaigns/{id}/analysis/benchmark` - Benchmark comparison

### AI Optimization
- `POST /api/campaigns/{id}/optimize/copy` - Optimize ad copy
- `POST /api/campaigns/{id}/predict` - Predict performance
- `POST /api/campaigns/{id}/optimize/bidding` - Optimize bidding

### Competitor Analysis
- `POST /api/competitor/analyze` - Analyze specific competitor
- `GET /api/competitor/category/{category}` - Monitor category competitors
- `POST /api/competitor/keywords/analyze` - Keyword competition analysis

### Automation
- `POST /api/automation/schedule` - Schedule automation task
- `GET /api/automation/tasks/{id}` - Get task status
- `DELETE /api/automation/tasks/{id}` - Cancel task
- `GET /api/automation/stats` - Scheduler statistics

### Health & Monitoring
- `GET /health` - Service health check
- `GET /api/info` - Service information
- `GET /metrics` - Service metrics

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Request throttling to prevent abuse
- **Input Validation**: Comprehensive data validation
- **CORS Protection**: Cross-origin request security
- **Security Headers**: XSS, CSRF, and other security headers
- **Request Logging**: Detailed request/response logging

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/ -k "test_campaign_manager"
```

## 📊 Monitoring & Health Checks

The service provides comprehensive monitoring:

- **Health Endpoint**: `/health` for basic health status
- **Metrics Endpoint**: `/metrics` for detailed performance metrics
- **Structured Logging**: JSON-formatted logs for analysis
- **Redis Health**: Cache and queue connectivity monitoring
- **Database Health**: PostgreSQL connection monitoring

## 🔄 Task Scheduling

The service includes a sophisticated task scheduling system:

- **Campaign Optimization**: Automated performance optimization
- **Performance Analysis**: Regular metrics analysis and insights
- **Competitor Monitoring**: Ongoing competitive intelligence
- **A/B Test Analysis**: Statistical significance testing
- **Budget Adjustment**: Performance-based budget optimization
- **Report Generation**: Automated reporting

## 🌟 Production Considerations

- Set strong `SECRET_KEY` environment variable
- Configure proper `DATABASE_URL` and `REDIS_URL`
- Set up monitoring and alerting
- Configure log aggregation
- Implement proper backup strategies
- Set resource limits in production
- Use load balancing for high availability

## 🚀 Service Port: 8014

The Campaign Automation Service runs on port **8014** and is accessible at:
- API Documentation: `http://localhost:8014/docs`
- Health Check: `http://localhost:8014/health`
- Service Info: `http://localhost:8014/api/info`

---

**Part of the Mercado Livre ML Automation System** 🇧🇷  
Developed by ML Project Team for production-ready campaign automation.