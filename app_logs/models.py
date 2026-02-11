from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class LogEntry:
    """Main log entry model"""
    type: str  # 'INFO', 'ERROR', 'DEBUG'
    function: Optional[str] = None
    file: Optional[str] = None
    err_type: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    lambda_function: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def get_tags_json(self) -> str:
        """Convert tags to JSON string"""
        if self.tags:
            return json.dumps(self.tags)
        return json.dumps({})


@dataclass
class LogDetails:
    """Log details model"""
    log_id: int
    messages: str
    stack_trace: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def get_stack_trace_json(self) -> str:
        """Convert stack_trace to JSON string"""
        if self.stack_trace:
            return json.dumps(self.stack_trace)
        return json.dumps({})

    def get_extra_json(self) -> str:
        """Convert extra to JSON string"""
        if self.extra:
            return json.dumps(self.extra)
        return json.dumps({})
