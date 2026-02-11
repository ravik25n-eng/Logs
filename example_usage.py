"""
Usage examples for app_logs package
"""

from app_logs import AppLogger

# Initialize the logger (optional: specify lambda_function name)
logger = AppLogger(lambda_function="my_lambda_function")

# Initialize database connections (do this once at application startup)
AppLogger.initialize_db(min_conn=1, max_conn=5)

try:
    # Example 1: Info logging
    log_id = logger.info(
        message="User login successful",
        tags={"user_id": 123, "ip_address": "192.168.1.1"},
        extra={"session_id": "abc123"}
    )
    print(f"Info log inserted with id: {log_id}")
    
    # Example 2: Debug logging
    log_id = logger.debug(
        message="Processing request with ID: xyz789",
        tags={"request_id": "xyz789"},
        extra={"duration_ms": 245}
    )
    print(f"Debug log inserted with id: {log_id}")
    
    # Example 3: Error logging
    try:
        # Some operation that fails
        result = 10 / 0
    except ZeroDivisionError as e:
        import traceback
        
        log_id = logger.error(
            message="Division by zero error occurred",
            err_type="ZeroDivisionError",
            tags={"operation": "division", "severity": "high"},
            stack_trace={
                "error": str(e),
                "traceback": traceback.format_exc()
            },
            extra={"numerator": 10, "denominator": 0}
        )
        print(f"Error log inserted with id: {log_id}")

finally:
    # Close all database connections (do this at application shutdown)
    AppLogger.close_db()
