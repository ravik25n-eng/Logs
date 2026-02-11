from typing import Optional, Dict, Any
from datetime import datetime
import traceback
import inspect

from .models import LogEntry, LogDetails
from .database import LogRepository, DatabaseConnection


class AppLogger:
    """Main logger class for application logging"""
    
    def __init__(self, lambda_function: Optional[str] = None):
        """
        Initialize logger
        
        Args:
            lambda_function: Optional name of lambda function
        """
        self.lambda_function = lambda_function
    
    def _get_caller_info(self) -> tuple:
        """Get caller file and function information"""
        frame = inspect.currentframe()
        try:
            # Skip frames: _get_caller_info -> _log -> info/error/debug -> user code
            caller_frame = frame.f_back.f_back.f_back
            filename = caller_frame.f_code.co_filename
            function_name = caller_frame.f_code.co_name
            return filename, function_name
        finally:
            del frame
    
    def _log(
        self,
        log_type: str,
        message: str,
        file: Optional[str] = None,
        function: Optional[str] = None,
        err_type: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Internal logging method
        
        Args:
            log_type: Type of log ('INFO', 'ERROR', 'DEBUG')
            message: Log message
            file: Source file path
            function: Function name
            err_type: Error type
            tags: Additional tags
            stack_trace: Stack trace info
            extra: Extra information
            
        Returns:
            log_id of inserted record
        """
        # Get caller info if not provided
        if not file or not function:
            caller_file, caller_function = self._get_caller_info()
            file = file or caller_file
            function = function or caller_function
        
        # Create log entry
        log_entry = LogEntry(
            type=log_type,
            function=function,
            file=file,
            err_type=err_type,
            tags=tags,
            lambda_function=self.lambda_function
        )
        
        # Create log details
        log_details = LogDetails(
            log_id=0,  # Will be set by database
            messages=message,
            stack_trace=stack_trace,
            extra=extra
        )
        
        # Insert to database
        log_id = LogRepository.insert_log_with_details(log_entry, log_details)
        return log_id
    
    def info(
        self,
        message: str,
        tags: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        file: Optional[str] = None,
        function: Optional[str] = None,
    ) -> int:
        """
        Log info level message
        
        Args:
            message: Log message
            tags: Additional tags
            extra: Extra information
            file: Source file (auto-detected if not provided)
            function: Function name (auto-detected if not provided)
            
        Returns:
            log_id of inserted record
        """
        return self._log(
            log_type="INFO",
            message=message,
            tags=tags,
            extra=extra,
            file=file,
            function=function
        )
    
    def error(
        self,
        message: str,
        err_type: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        file: Optional[str] = None,
        function: Optional[str] = None,
    ) -> int:
        """
        Log error level message
        
        Args:
            message: Error message
            err_type: Type of error
            tags: Additional tags
            stack_trace: Stack trace info
            extra: Extra information
            file: Source file (auto-detected if not provided)
            function: Function name (auto-detected if not provided)
            
        Returns:
            log_id of inserted record
        """
        return self._log(
            log_type="ERROR",
            message=message,
            err_type=err_type,
            tags=tags,
            stack_trace=stack_trace,
            extra=extra,
            file=file,
            function=function
        )
    
    def debug(
        self,
        message: str,
        tags: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        file: Optional[str] = None,
        function: Optional[str] = None,
    ) -> int:
        """
        Log debug level message
        
        Args:
            message: Debug message
            tags: Additional tags
            extra: Extra information
            file: Source file (auto-detected if not provided)
            function: Function name (auto-detected if not provided)
            
        Returns:
            log_id of inserted record
        """
        return self._log(
            log_type="DEBUG",
            message=message,
            tags=tags,
            extra=extra,
            file=file,
            function=function
        )
    
    @staticmethod
    def initialize_db(min_conn: int = 1, max_conn: int = 5) -> None:
        """
        Initialize database connection pool
        
        Args:
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        DatabaseConnection.initialize_pool(min_conn, max_conn)
    
    @staticmethod
    def close_db() -> None:
        """Close all database connections"""
        DatabaseConnection.close_all()
