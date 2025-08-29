"""
Unit tests for error handling system
"""

import time
from unittest.mock import Mock, patch

import pytest

from utils.error_handling import (
    ConfigurationError,
    ErrorHandler,
    ErrorSeverity,
    ExchangeConnectionError,
    InsufficientFundsError,
    InvalidTradeSignalError,
    PerformanceMonitor,
    RiskLimitExceededError,
    TradingError,
    monitor_performance,
    with_error_handling,
    with_retry,
)


@pytest.mark.unit
class TestTradingError:
    """Test cases for TradingError and subclasses"""

    def test_trading_error_creation(self):
        """Test creating a TradingError"""
        error = TradingError("Test error", ErrorSeverity.HIGH, {"key": "value"})

        assert str(error) == "Test error"
        assert error.severity == ErrorSeverity.HIGH
        assert error.context == {"key": "value"}
        assert error.timestamp is not None

    def test_trading_error_defaults(self):
        """Test TradingError with default values"""
        error = TradingError("Test error")

        assert error.severity == ErrorSeverity.MEDIUM
        assert error.context == {}

    def test_specialized_errors(self):
        """Test specialized error classes"""
        exchange_error = ExchangeConnectionError("Connection failed")
        assert isinstance(exchange_error, TradingError)

        funds_error = InsufficientFundsError("Not enough funds")
        assert isinstance(funds_error, TradingError)

        signal_error = InvalidTradeSignalError("Invalid signal")
        assert isinstance(signal_error, TradingError)

        risk_error = RiskLimitExceededError("Risk exceeded")
        assert isinstance(risk_error, TradingError)

        config_error = ConfigurationError("Config error")
        assert isinstance(config_error, TradingError)


@pytest.mark.unit
class TestErrorHandler:
    """Test cases for ErrorHandler class"""

    def test_handle_trading_error(self):
        """Test handling TradingError"""
        handler = ErrorHandler()
        error = TradingError("Test error", ErrorSeverity.HIGH, {"test": "context"})

        with patch.object(handler.logger, "error") as mock_log:
            handler.handle_error(error)

            # High severity errors log twice: once for the error, once for stack trace
            assert mock_log.call_count == 2
            assert "Test error" in str(mock_log.call_args_list[0])

    def test_handle_generic_error(self):
        """Test handling generic exception"""
        handler = ErrorHandler()
        error = ValueError("Generic error")

        with patch.object(handler.logger, "warning") as mock_log:
            handler.handle_error(error)

            mock_log.assert_called_once()
            assert "Generic error" in str(mock_log.call_args)

    def test_error_counting(self):
        """Test error counting functionality"""
        handler = ErrorHandler()

        # Handle multiple errors of same type
        for _ in range(3):
            handler.handle_error(ValueError("Test"))

        # Handle different error type
        handler.handle_error(TypeError("Different error"))

        summary = handler.get_error_summary()
        assert summary["error_counts"]["ValueError"] == 3
        assert summary["error_counts"]["TypeError"] == 1
        assert summary["total_errors"] == 4

    def test_severity_determination(self):
        """Test automatic severity determination"""
        handler = ErrorHandler()

        # Connection errors should be HIGH
        assert handler._determine_severity(ConnectionError()) == ErrorSeverity.HIGH

        # Value errors should be MEDIUM
        assert handler._determine_severity(ValueError()) == ErrorSeverity.MEDIUM

        # Keyboard interrupt should be LOW
        assert handler._determine_severity(KeyboardInterrupt()) == ErrorSeverity.LOW

    def test_get_error_summary(self):
        """Test getting error summary"""
        handler = ErrorHandler()

        # Initially empty
        summary = handler.get_error_summary()
        assert summary["total_errors"] == 0
        assert summary["error_counts"] == {}

        # After handling errors
        handler.handle_error(ValueError("Test"))
        summary = handler.get_error_summary()
        assert summary["total_errors"] == 1
        assert "ValueError" in summary["error_counts"]


@pytest.mark.unit
class TestErrorHandlingDecorator:
    """Test cases for error handling decorator"""

    def test_with_error_handling_reraise(self):
        """Test error handling decorator with reraise=True"""

        @with_error_handling(error_types=(ValueError,), reraise=True)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    def test_with_error_handling_no_reraise(self):
        """Test error handling decorator with reraise=False"""

        @with_error_handling(
            error_types=(ValueError,), reraise=False, default_return="default"
        )
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        assert result == "default"

    def test_with_error_handling_success(self):
        """Test error handling decorator with successful function"""

        @with_error_handling()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_with_error_handling_context(self):
        """Test error handling decorator adds function context"""

        @with_error_handling(reraise=False)
        def test_function(arg1, kwarg1=None):
            raise ValueError("Test error")

        # Should not raise due to reraise=False
        test_function("value", kwarg1="keyword")


@pytest.mark.unit
class TestRetryDecorator:
    """Test cases for retry decorator"""

    def test_with_retry_success_first_attempt(self):
        """Test retry decorator when function succeeds on first attempt"""

        @with_retry(max_attempts=3)
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_with_retry_success_after_failures(self):
        """Test retry decorator when function succeeds after failures"""
        call_count = 0

        @with_retry(max_attempts=3, delay=0.1)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_with_retry_all_attempts_fail(self):
        """Test retry decorator when all attempts fail"""

        @with_retry(max_attempts=2, delay=0.1)
        def always_failing_function():
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            always_failing_function()

    def test_with_retry_non_retryable_exception(self):
        """Test retry decorator with non-retryable exception"""

        @with_retry(max_attempts=3, exceptions=(ConnectionError,))
        def function_with_value_error():
            raise ValueError("Not retryable")

        with pytest.raises(ValueError):
            function_with_value_error()

    def test_with_retry_exponential_backoff(self):
        """Test retry decorator with exponential backoff"""
        call_times = []

        @with_retry(max_attempts=3, delay=0.1, exponential_backoff=True)
        def function_with_timing():
            call_times.append(time.time())
            raise ConnectionError("Test")

        with pytest.raises(ConnectionError):
            function_with_timing()

        # Should have 3 attempts (no delay before first, then delays)
        assert len(call_times) == 3


@pytest.mark.unit
class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor class"""

    def test_record_metric(self):
        """Test recording performance metrics"""
        monitor = PerformanceMonitor()

        monitor.record_metric("test_metric", 5.0)
        monitor.record_metric("test_metric", 3.0)

        summary = monitor.get_metric_summary("test_metric")
        assert summary["count"] == 2
        assert summary["min"] == 3.0
        assert summary["max"] == 5.0
        assert summary["avg"] == 4.0
        assert summary["latest"] == 3.0

    def test_metric_threshold_checking(self):
        """Test metric threshold checking"""
        monitor = PerformanceMonitor()
        monitor.set_threshold("test_metric", 10.0)

        with patch.object(monitor.logger, "warning") as mock_log:
            monitor.record_metric("test_metric", 15.0)  # Exceeds threshold
            mock_log.assert_called_once()

            mock_log.reset_mock()
            monitor.record_metric("test_metric", 5.0)  # Within threshold
            mock_log.assert_not_called()

    def test_metric_history_limit(self):
        """Test metric history is limited to 100 entries"""
        monitor = PerformanceMonitor()

        # Record more than 100 metrics
        for i in range(150):
            monitor.record_metric("test_metric", float(i))

        summary = monitor.get_metric_summary("test_metric")
        assert summary["count"] == 100
        assert summary["min"] == 50.0  # Should start from 50 (150-100)
        assert summary["max"] == 149.0

    def test_get_metric_summary_nonexistent(self):
        """Test getting summary for non-existent metric"""
        monitor = PerformanceMonitor()

        summary = monitor.get_metric_summary("nonexistent")
        assert summary is None

    def test_set_threshold(self):
        """Test setting custom thresholds"""
        monitor = PerformanceMonitor()

        with patch.object(monitor.logger, "info") as mock_log:
            monitor.set_threshold("custom_metric", 100.0)

            assert monitor.thresholds["custom_metric"] == 100.0
            mock_log.assert_called_once()


@pytest.mark.unit
class TestPerformanceMonitorDecorator:
    """Test cases for performance monitoring decorator"""

    def test_monitor_performance_success(self):
        """Test performance monitoring decorator with successful function"""

        @monitor_performance("test_function")
        def test_function():
            time.sleep(0.1)  # Simulate some work
            return "result"

        result = test_function()
        assert result == "result"

        # Check that metric was recorded
        summary = test_function._monitor.get_metric_summary("test_function")
        assert summary is not None
        assert summary["count"] == 1
        assert summary["latest"] >= 0.1  # Should be at least 0.1 seconds

    def test_monitor_performance_with_exception(self):
        """Test performance monitoring decorator when function raises exception"""

        @monitor_performance("test_function")
        def failing_function():
            time.sleep(0.05)
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Check that error metric was recorded
        summary = failing_function._monitor.get_metric_summary("test_function_error")
        assert summary is not None
        assert summary["count"] == 1
        assert summary["latest"] >= 0.05

    def test_monitor_performance_multiple_calls(self):
        """Test performance monitoring with multiple function calls"""

        @monitor_performance("multi_call")
        def test_function():
            return "result"

        # Call multiple times
        for _ in range(5):
            test_function()

        summary = test_function._monitor.get_metric_summary("multi_call")
        assert summary["count"] == 5
