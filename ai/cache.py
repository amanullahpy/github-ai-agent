import hashlib
import json
from typing import Optional, Dict, Any
from database import Database, get_db
from database.models import AIUsage


class AICache:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    @staticmethod
    def compute_input_hash(operation: str, prompt: str, context: Dict[str, Any]) -> str:
        payload = f"{operation}:{prompt}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record_usage(
        self,
        operation: str,
        model: str,
        input_hash: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        estimated_cost: float = 0.0,
        repository_id: Optional[int] = None,
        success: bool = True
    ) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO ai_usage (operation, repository_id, model, input_hash, input_tokens, output_tokens, estimated_cost, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (operation, repository_id, model, input_hash, input_tokens, output_tokens, estimated_cost, int(success))
            )
            conn.commit()
