"""
app_logs - Application Logging Package

A Python package for inserting application logs into PostgreSQL database
with support for INFO, ERROR, and DEBUG log levels.
"""

from .logger import AppLogger
from .models import LogEntry, LogDetails
from .database import DatabaseConnection, LogRepository

__version__ = "0.1.0"
__author__ = "Ravi K"

__all__ = [
    "AppLogger",
    "LogEntry",
    "LogDetails",
    "DatabaseConnection",
    "LogRepository",
]
