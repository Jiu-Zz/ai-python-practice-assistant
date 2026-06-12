from typing import Any, Dict, Optional
from uuid import uuid4


def api_response(data: Any = None, message: str = "ok", trace_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "message": message,
        "trace_id": trace_id or f"req-{uuid4().hex[:12]}",
    }


def error_response(message: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "message": message,
        "trace_id": trace_id or f"req-{uuid4().hex[:12]}",
    }
