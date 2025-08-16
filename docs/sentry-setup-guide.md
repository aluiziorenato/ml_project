# Sentry Setup Guide for ML Project Backend

## Overview
This guide explains how to set up Sentry error monitoring for the ML Project backend with GitHub Actions integration.

## Prerequisites
- Sentry account (free tier available at [sentry.io](https://sentry.io))
- GitHub repository with admin access to configure secrets

## Step 1: Create Sentry Project

1. Log in to [sentry.io](https://sentry.io)
2. Create a new project
3. Select "Python" as the platform
4. Select "FastAPI" as the framework
5. Copy the DSN (Data Source Name) - it looks like: `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`

## Step 2: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to Repository → Settings → Secrets and variables → Actions
2. Add these secrets:

```
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

Optional secrets for fine-tuning:
```
SENTRY_ENVIRONMENT=production  # Will auto-set based on branch
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions for performance monitoring
```

## Step 3: Environment Configuration

The backend automatically configures Sentry based on environment variables:

- `SENTRY_DSN`: Your Sentry project DSN (required)
- `SENTRY_ENVIRONMENT`: Environment name (auto-detected from git branch)
- `SENTRY_TRACES_SAMPLE_RATE`: Performance monitoring sample rate (default: 0.1)

## Step 4: Usage in Code

Sentry is automatically initialized when the application starts. You can use these functions:

```python
from app.monitoring.sentry_config import capture_message, capture_exception, add_breadcrumb

# Capture custom messages
capture_message("User action completed", level="info", user_id=123)

# Capture exceptions with context
try:
    risky_operation()
except Exception as e:
    capture_exception(e, user_id=123, operation="risky_operation")

# Add debugging breadcrumbs
add_breadcrumb("Starting API call", category="api", data={"endpoint": "/users"})
```

## Step 5: Verify Setup

1. Deploy your application with Sentry configuration
2. Trigger an error or send a test message
3. Check your Sentry dashboard for the event

## Features Enabled

### Error Tracking
- Automatic exception capture
- Stack traces with source code
- Error grouping and deduplication

### Performance Monitoring
- API endpoint response times
- Database query performance
- External API call tracking

### Integrations
- FastAPI automatic instrumentation
- SQLAlchemy database monitoring
- HTTPX HTTP client monitoring
- Logging integration

### Context Information
- User information (if available)
- Request details
- Custom tags and metadata
- Environment information

## Environment-Specific Configuration

### Development
- Lower sample rates to reduce noise
- More detailed logging
- Local testing with console output

### Production
- Higher sample rates for better coverage
- Alert configuration for critical errors
- Performance threshold monitoring

## Troubleshooting

### Sentry Not Capturing Events
1. Verify `SENTRY_DSN` is correctly set
2. Check application logs for Sentry initialization messages
3. Ensure network connectivity to Sentry servers

### Too Many Events
1. Adjust `SENTRY_TRACES_SAMPLE_RATE` to lower value
2. Configure Sentry filters to exclude noisy errors
3. Use environment-specific configurations

### Missing Context
1. Add custom breadcrumbs before operations
2. Set user context in authentication middleware
3. Include relevant metadata in error captures

## Best Practices

1. **Don't send PII**: Configure Sentry to exclude sensitive data
2. **Use appropriate sample rates**: Balance monitoring coverage with performance
3. **Add context**: Include relevant information with error captures
4. **Set up alerts**: Configure notifications for critical errors
5. **Review regularly**: Monitor Sentry dashboard for trends and issues

## Example Alert Configuration

Set up alerts in Sentry for:
- Error rate > 5% in 5 minutes
- New error types
- Performance degradation > 2x baseline
- Critical errors in production

## Integration with CI/CD

The CI/CD pipeline automatically:
- Sets up Sentry configuration based on environment
- Tests Sentry integration during backend tests
- Deploys with proper environment configuration
- Validates error monitoring functionality