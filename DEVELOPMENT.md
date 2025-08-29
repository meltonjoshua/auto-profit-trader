# Auto Profit Trader - Development Guide

## Code Quality Standards

This project maintains enterprise-grade code quality standards with comprehensive testing, security practices, and documentation.

### Testing Infrastructure

#### Coverage Requirements
- **Minimum Coverage**: 80% for new code
- **Current Coverage**: 28% overall (focused on core utilities)
- **Test Types**: Unit tests, integration tests, security tests

#### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/utils/ -v          # Utils tests
pytest tests/unit/security/ -v       # Security tests

# Run tests with markers
pytest -m unit                       # Unit tests only
pytest -m integration               # Integration tests only
pytest -m slow                      # Slow tests only
```

#### Test Structure
```
tests/
├── conftest.py                      # Shared fixtures
├── unit/                           # Unit tests
│   ├── utils/                      # Utility function tests
│   ├── security/                   # Security system tests
│   ├── core/                       # Core trading logic tests
│   └── ...
└── integration/                    # Integration tests
    ├── exchange_integration/       # Exchange API tests
    └── end_to_end/                # Full system tests
```

### Code Quality Tools

#### Linting and Formatting
```bash
# Format code
black src/ tests/ --line-length=88

# Sort imports
isort src/ tests/ --profile black

# Lint code
flake8 src/ --max-line-length=88

# Type checking
mypy src/ --ignore-missing-imports

# Security scanning
bandit -r src/ -f json -o bandit-report.json
```

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Security Standards

#### Credential Management
- All API keys are encrypted using Fernet symmetric encryption
- Encryption keys are stored with 600 permissions (owner read/write only)
- No credentials are stored in plain text or environment variables
- Automatic security validation on startup

#### Input Validation
- All external inputs are validated using the `InputValidator` class
- Trading signals are validated before execution
- Configuration values are validated on load
- API responses are sanitized before processing

#### Error Handling
- Custom exception hierarchy for trading-specific errors
- Comprehensive error logging with context
- Automatic retry mechanisms for transient failures
- Performance monitoring and alerting

### Performance Standards

#### Response Time Requirements
- API calls: < 5 seconds
- Trade execution: < 2 seconds
- Risk assessment: < 1 second

#### Memory Usage
- Maximum heap size: 500MB
- Automatic memory cleanup for sensitive data
- Performance monitoring with thresholds

#### Monitoring
```python
from utils.error_handling import monitor_performance

@monitor_performance("trade_execution")
async def execute_trade(signal):
    # Trading logic here
    pass
```

### Development Workflow

#### 1. Feature Development
1. Create feature branch from `main`
2. Write tests first (TDD approach)
3. Implement feature with proper error handling
4. Add comprehensive documentation
5. Run all quality checks
6. Create pull request

#### 2. Code Review Checklist
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities
- [ ] Proper error handling
- [ ] Type hints included
- [ ] Documentation updated
- [ ] Performance impact assessed

#### 3. Release Process
1. Run full test suite
2. Security scan
3. Performance benchmarks
4. Update version numbers
5. Create release notes
6. Deploy to staging
7. Integration tests
8. Deploy to production

### Architecture Standards

#### Error Handling Pattern
```python
from utils.error_handling import with_error_handling, with_retry
from utils.validators import InputValidator

@with_retry(max_attempts=3)
@with_error_handling(error_types=(ExchangeConnectionError,))
async def get_market_data(symbol: str) -> Dict[str, Any]:
    # Validate input
    if not InputValidator.validate_trading_pair(symbol):
        raise InvalidTradeSignalError(f"Invalid symbol: {symbol}")
    
    # Implementation here
    pass
```

#### Logging Pattern
```python
import logging
from utils.logger import setup_logger

logger = setup_logger(__name__)

def process_trade():
    logger.info("Starting trade processing")
    try:
        # Trade logic
        logger.debug("Trade executed successfully")
    except Exception as e:
        logger.error("Trade failed: %s", e, exc_info=True)
        raise
```

#### Configuration Pattern
```python
from utils.config_manager import ConfigManager
from utils.validators import InputValidator

config_manager = ConfigManager()
trading_config = config_manager.get_section("trading")

# Validate configuration
errors = InputValidator.validate_config_section(
    trading_config, 
    ["daily_loss_limit", "max_position_size"]
)
if errors:
    raise ConfigurationError(f"Invalid config: {errors}")
```

### Security Guidelines

#### 1. Credential Security
- Never hardcode API keys or secrets
- Use environment variables for non-production environments only
- Encrypt all stored credentials
- Regularly rotate API keys
- Use read-only API permissions when possible

#### 2. Input Validation
- Validate all external inputs
- Sanitize strings to prevent injection
- Check numeric ranges and formats
- Validate trading pairs and amounts

#### 3. Error Information
- Never log sensitive information
- Use error codes instead of detailed messages in production
- Hash sensitive data for identification purposes

### Testing Guidelines

#### 1. Unit Tests
- Test each function/method in isolation
- Mock external dependencies
- Cover edge cases and error conditions
- Aim for 100% coverage on new code

#### 2. Integration Tests
- Test component interactions
- Use test doubles for external services
- Validate configuration loading
- Test error propagation

#### 3. Security Tests
- Test encryption/decryption roundtrips
- Validate input sanitization
- Test permission checking
- Verify secure file operations

### CI/CD Pipeline

#### GitHub Actions Workflow
- **Multi-Python Testing**: Tests run on Python 3.8, 3.9, 3.10, 3.11
- **Code Quality**: Black, isort, flake8, mypy checks
- **Security Scanning**: Bandit security analysis, safety dependency checks
- **Test Coverage**: Pytest with coverage reporting
- **Artifact Generation**: Coverage reports, security reports

#### Quality Gates
- All tests must pass
- Code coverage > 80%
- No high-severity security issues
- All linting checks pass
- Type checking passes

### Documentation Standards

#### 1. Code Documentation
- All public functions have docstrings
- Type hints for all parameters and return values
- Examples for complex functions
- Security considerations noted

#### 2. API Documentation
- All endpoints documented
- Request/response schemas
- Error codes and meanings
- Rate limiting information

#### 3. User Documentation
- Installation guide
- Configuration reference
- Troubleshooting guide
- Security best practices

### Performance Optimization

#### 1. Database Operations
- Use connection pooling
- Implement query optimization
- Add appropriate indexes
- Monitor query performance

#### 2. Memory Management
- Avoid memory leaks
- Use generators for large datasets
- Implement caching strategically
- Monitor memory usage

#### 3. Network Operations
- Use connection pooling
- Implement request retry logic
- Add appropriate timeouts
- Monitor latency

This development guide ensures that the Auto Profit Trader maintains enterprise-grade quality standards while being maintainable and secure.