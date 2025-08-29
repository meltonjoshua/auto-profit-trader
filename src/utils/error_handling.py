"""
Enhanced error handling and monitoring for Auto Profit Trader
"""

import functools
import logging
import sys
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, Union


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TradingError(Exception):
    """Base exception for trading-related errors"""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.severity = severity
        self.context = context or {}
        self.timestamp = datetime.now()


class ExchangeConnectionError(TradingError):
    """Error connecting to exchange"""

    pass


class InsufficientFundsError(TradingError):
    """Insufficient funds for trade"""

    pass


class InvalidTradeSignalError(TradingError):
    """Invalid trade signal data"""

    pass


class RiskLimitExceededError(TradingError):
    """Risk management limits exceeded"""

    pass


class ConfigurationError(TradingError):
    """Configuration-related error"""

    pass


class ErrorHandler:
    """Enhanced error handling with context and recovery strategies"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}

    def handle_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle an error with appropriate logging and context

        Args:
            error: The exception that occurred
            context: Additional context information
        """
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_errors[error_type] = datetime.now()

        context = context or {}

        # Determine severity
        if isinstance(error, TradingError):
            severity = error.severity
            context.update(error.context)
        else:
            severity = self._determine_severity(error)

        # Log with appropriate level
        log_method = self._get_log_method(severity)
        log_method(
            "Error occurred: %s | Type: %s | Context: %s | Count: %d",
            str(error),
            error_type,
            context,
            self.error_counts[error_type],
        )

        # Log stack trace for high/critical errors
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error("Stack trace: %s", traceback.format_exc())

    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on exception type"""
        if isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorSeverity.HIGH
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, KeyboardInterrupt):
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM

    def _get_log_method(self, severity: ErrorSeverity) -> Callable:
        """Get appropriate logging method for severity"""
        severity_map = {
            ErrorSeverity.LOW: self.logger.info,
            ErrorSeverity.MEDIUM: self.logger.warning,
            ErrorSeverity.HIGH: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical,
        }
        return severity_map[severity]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            "error_counts": self.error_counts.copy(),
            "last_errors": {k: v.isoformat() for k, v in self.last_errors.items()},
            "total_errors": sum(self.error_counts.values()),
        }


def with_error_handling(
    error_types: Optional[tuple] = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    reraise: bool = True,
    default_return: Any = None,
):
    """
    Decorator for automatic error handling

    Args:
        error_types: Tuple of exception types to catch
        severity: Default severity for caught errors
        reraise: Whether to reraise the exception after handling
        default_return: Default value to return if error is caught and not reraised
    """
    if error_types is None:
        error_types = (Exception,)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                # Create error handler if not exists
                if not hasattr(wrapper, "_error_handler"):
                    wrapper._error_handler = ErrorHandler()

                # Add function context
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }

                # Handle the error
                if isinstance(e, TradingError):
                    wrapper._error_handler.handle_error(e, context)
                else:
                    # Convert to TradingError
                    trading_error = TradingError(str(e), severity, context)
                    wrapper._error_handler.handle_error(trading_error, context)

                if reraise:
                    raise
                else:
                    return default_return

        return wrapper

    return decorator


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exponential_backoff: bool = True,
    exceptions: Optional[tuple] = None,
):
    """
    Decorator for automatic retry logic

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        exponential_backoff: Whether to use exponential backoff
        exceptions: Tuple of exception types that trigger retry
    """
    if exceptions is None:
        exceptions = (ConnectionError, TimeoutError)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        # Last attempt, don't delay
                        break

                    # Calculate delay
                    current_delay = delay
                    if exponential_backoff:
                        current_delay = delay * (2**attempt)

                    logger = logging.getLogger(func.__module__)
                    logger.warning(
                        "Attempt %d/%d failed for %s: %s. Retrying in %.1f seconds...",
                        attempt + 1,
                        max_attempts,
                        func.__name__,
                        str(e),
                        current_delay,
                    )

                    time.sleep(current_delay)

            # All attempts failed
            raise last_exception

        return wrapper

    return decorator


class PerformanceMonitor:
    """Monitor performance metrics and detect anomalies"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, list] = {}
        self.thresholds: Dict[str, float] = {
            "execution_time": 10.0,  # seconds
            "memory_usage": 500.0,  # MB
            "error_rate": 0.1,  # 10%
        }

    def record_metric(self, name: str, value: float) -> None:
        """Record a performance metric"""
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append({"value": value, "timestamp": datetime.now()})

        # Keep only last 100 measurements
        if len(self.metrics[name]) > 100:
            self.metrics[name] = self.metrics[name][-100:]

        # Check for threshold violations
        self._check_threshold(name, value)

    def _check_threshold(self, name: str, value: float) -> None:
        """Check if metric exceeds threshold"""
        threshold = self.thresholds.get(name)
        if threshold and value > threshold:
            self.logger.warning(
                "Performance threshold exceeded: %s = %.2f (threshold: %.2f)",
                name,
                value,
                threshold,
            )

    def get_metric_summary(self, name: str) -> Optional[Dict[str, float]]:
        """Get summary statistics for a metric"""
        if name not in self.metrics or not self.metrics[name]:
            return None

        values = [m["value"] for m in self.metrics[name]]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
        }

    def set_threshold(self, name: str, threshold: float) -> None:
        """Set performance threshold for a metric"""
        self.thresholds[name] = threshold
        self.logger.info("Set performance threshold: %s = %.2f", name, threshold)


def monitor_performance(metric_name: str):
    """
    Decorator to monitor function execution time

    Args:
        metric_name: Name of the metric to record
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            if not hasattr(wrapper, "_monitor"):
                wrapper._monitor = PerformanceMonitor()

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                wrapper._monitor.record_metric(metric_name, execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                wrapper._monitor.record_metric(f"{metric_name}_error", execution_time)
                raise

        return wrapper

    return decorator


# Global error handler instance
global_error_handler = ErrorHandler()
global_performance_monitor = PerformanceMonitor()


def log_exception(
    exc_type: Type[BaseException], exc_value: BaseException, exc_traceback
) -> None:
    """Global exception handler for uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger("global")
    logger.critical(
        "Uncaught exception: %s",
        "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
    )

    # Handle through global error handler
    global_error_handler.handle_error(
        exc_value,
        {
            "type": "uncaught_exception",
            "module": getattr(exc_value, "__module__", "unknown"),
        },
    )


# Install global exception handler
sys.excepthook = log_exception
