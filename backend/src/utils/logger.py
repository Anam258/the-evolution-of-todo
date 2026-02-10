"""
Logging utilities for the backend application.
Provides structured logging with request context.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import traceback
import sys


class ContextualLogger:
    """
    A logger that adds contextual information to log messages.
    """

    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)

        # Set up basic configuration if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _format_log_entry(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a log entry with contextual information.

        Args:
            level: Log level
            message: Log message
            context: Additional context to include in the log

        Returns:
            Formatted log entry
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "context": context or {}
        }

        return json.dumps(log_entry)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message with context.

        Args:
            message: Log message
            context: Additional context to include in the log
        """
        formatted_msg = self._format_log_entry("INFO", message, context)
        self.logger.info(formatted_msg)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning message with context.

        Args:
            message: Log message
            context: Additional context to include in the log
        """
        formatted_msg = self._format_log_entry("WARNING", message, context)
        self.logger.warning(formatted_msg)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error message with context.

        Args:
            message: Log message
            context: Additional context to include in the log
        """
        formatted_msg = self._format_log_entry("ERROR", message, context)
        self.logger.error(formatted_msg)

    def exception(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an exception with traceback and context.

        Args:
            message: Log message
            context: Additional context to include in the log
        """
        tb_str = traceback.format_exc()
        if context is None:
            context = {}
        context["traceback"] = tb_str

        formatted_msg = self._format_log_entry("EXCEPTION", message, context)
        self.logger.error(formatted_msg)


# Global logger instance
logger = ContextualLogger("todo_api")


def log_request_context(func):
    """
    Decorator to add request context to log messages.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        # Add request context to logs
        # This would be enhanced in a real implementation with actual request data
        logger.info(f"Executing function: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.exception(f"Error in function {func.__name__}: {str(e)}")
            raise

    return wrapper


def log_api_call(endpoint: str, method: str = "GET", user_id: Optional[int] = None):
    """
    Log an API call with context.

    Args:
        endpoint: API endpoint being called
        method: HTTP method being used
        user_id: ID of the authenticated user (if any)
    """
    context = {
        "endpoint": endpoint,
        "method": method.upper(),
        "user_id": user_id
    }

    logger.info("API call initiated", context)


def log_authentication_event(event_type: str, user_identifier: str = "", success: bool = True, ip_address: str = ""):
    """
    Log an authentication-related event.

    Args:
        event_type: Type of authentication event (login, logout, register, etc.)
        user_identifier: Identifier for the user (email, username, etc.)
        success: Whether the authentication event was successful
        ip_address: IP address of the request
    """
    context = {
        "event_type": event_type,
        "user_identifier": user_identifier,
        "success": success,
        "ip_address": ip_address
    }

    level = "info" if success else "warning"
    message = f"Authentication {event_type} {'successful' if success else 'failed'}"

    if success:
        logger.info(message, context)
    else:
        logger.warning(message, context)


def log_security_event(event_type: str, details: Dict[str, Any]):
    """
    Log a security-related event.

    Args:
        event_type: Type of security event
        details: Details about the security event
    """
    context = {
        "event_type": event_type,
        "details": details
    }

    logger.warning(f"Security event: {event_type}", context)


def log_database_operation(operation: str, table: str, success: bool = True, rows_affected: int = 0):
    """
    Log a database operation.

    Args:
        operation: Type of database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table being operated on
        success: Whether the operation was successful
        rows_affected: Number of rows affected by the operation
    """
    context = {
        "operation": operation.upper(),
        "table": table,
        "success": success,
        "rows_affected": rows_affected
    }

    level = "info" if success else "error"
    message = f"Database {operation} on {table} {'succeeded' if success else 'failed'}"

    if success:
        logger.info(message, context)
    else:
        logger.error(message, context)