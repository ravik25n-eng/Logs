import psycopg2
from psycopg2 import pool
from typing import Optional, Tuple
from datetime import datetime
import json

from .config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    LOG_TABLE, LOG_DETAILS_TABLE
)
from .models import LogEntry, LogDetails


class DatabaseConnection:
    """Manages database connections"""
    
    _connection_pool: Optional[pool.SimpleConnectionPool] = None
    
    @classmethod
    def initialize_pool(cls, min_conn: int = 1, max_conn: int = 5) -> None:
        """Initialize connection pool"""
        try:
            cls._connection_pool = pool.SimpleConnectionPool(
                min_conn,
                max_conn,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
        except Exception as e:
            raise Exception(f"Failed to initialize connection pool: {str(e)}")
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return connection to pool"""
        if cls._connection_pool:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    def close_all(cls) -> None:
        """Close all connections in pool"""
        if cls._connection_pool:
            cls._connection_pool.closeall()


class LogRepository:
    """Repository for log operations"""
    
    @staticmethod
    def insert_log(log_entry: LogEntry) -> int:
        """
        Insert main log entry
        
        Args:
            log_entry: LogEntry object
            
        Returns:
            log_id of the inserted record
        """
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            query = f"""
                INSERT INTO {LOG_TABLE} 
                (type, function, file, err_type, tags, lambda_function, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING log_id
            """
            
            cursor.execute(
                query,
                (
                    log_entry.type,
                    log_entry.function,
                    log_entry.file,
                    log_entry.err_type,
                    log_entry.get_tags_json(),
                    log_entry.lambda_function,
                    log_entry.timestamp or datetime.now()
                )
            )
            
            log_id = cursor.fetchone()[0]
            conn.commit()
            return log_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Failed to insert log: {str(e)}")
        finally:
            if conn:
                DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def insert_log_details(log_details: LogDetails) -> None:
        """
        Insert log details
        
        Args:
            log_details: LogDetails object
        """
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            query = f"""
                INSERT INTO {LOG_DETAILS_TABLE}
                (log_id, messages, stack_trace, extra)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(
                query,
                (
                    log_details.log_id,
                    log_details.messages,
                    log_details.get_stack_trace_json(),
                    log_details.get_extra_json()
                )
            )
            
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Failed to insert log details: {str(e)}")
        finally:
            if conn:
                DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def insert_log_with_details(log_entry: LogEntry, log_details: LogDetails) -> int:
        """
        Insert both main log and log details in a transaction
        
        Args:
            log_entry: LogEntry object
            log_details: LogDetails object (log_id will be overwritten)
            
        Returns:
            log_id of the inserted record
        """
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            # Insert main log
            query = f"""
                INSERT INTO {LOG_TABLE} 
                (type, function, file, err_type, tags, lambda_function, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING log_id
            """
            
            cursor.execute(
                query,
                (
                    log_entry.type,
                    log_entry.function,
                    log_entry.file,
                    log_entry.err_type,
                    log_entry.get_tags_json(),
                    log_entry.lambda_function,
                    log_entry.timestamp or datetime.now()
                )
            )
            
            log_id = cursor.fetchone()[0]
            log_details.log_id = log_id
            
            # Insert log details
            details_query = f"""
                INSERT INTO {LOG_DETAILS_TABLE}
                (log_id, messages, stack_trace, extra)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(
                details_query,
                (
                    log_details.log_id,
                    log_details.messages,
                    log_details.get_stack_trace_json(),
                    log_details.get_extra_json()
                )
            )
            
            conn.commit()
            return log_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Failed to insert log with details: {str(e)}")
        finally:
            if conn:
                DatabaseConnection.return_connection(conn)
