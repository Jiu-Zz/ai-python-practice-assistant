from typing import Any, Dict


class LlmClient:
    """A replaceable interface for future model providers.

    The first course-friendly implementation deliberately returns an empty
    response so the service layer uses deterministic local templates. Replacing
    this class with a real provider should not affect routers or frontend code.
    """

    def complete_json(self, system_prompt: str, user_prompt: str, schema_name: str) -> Dict[str, Any]:
        return {}
