#!/bin/bash
# Script to check coverage for specific target modules that should have 100% coverage

echo "Checking coverage for target modules..."

# Run tests and generate coverage data
python -m pytest tests/test_auth_token_coverage.py tests/test_auth_init_coverage.py tests/test_db_coverage.py tests/test_startup_coverage.py \
  --cov=app.auth.token --cov=app.auth --cov=app.db --cov=app.startup \
  --cov-report=term-missing --cov-fail-under=100

COVERAGE_EXIT_CODE=$?

if [ $COVERAGE_EXIT_CODE -eq 0 ]; then
    echo "✅ SUCCESS: All target modules have 100% coverage!"
    echo "Target modules:"
    echo "  - app/auth/token.py: 100%"
    echo "  - app/auth/__init__.py: 100%"
    echo "  - app/db.py: 100%"
    echo "  - app/startup.py: 100%"
else
    echo "❌ FAILURE: Target modules do not have 100% coverage"
    exit 1
fi

echo ""
echo "Running full test suite for overall project health..."
python -m pytest --cov=app --cov-report=term-missing --tb=short

echo ""
echo "📊 Coverage Summary:"
echo "✅ Critical auth and database modules: 100% coverage achieved"
echo "📈 Overall project coverage can be improved incrementally"