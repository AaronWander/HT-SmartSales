#2027-05-04-zty-start
"""Presales state persistence helpers.

The current presales flow relies primarily on natural-language confirmation.
This module stores and restores the presales runtime state from SessionDB meta.
"""

from __future__ import annotations

import json
from typing import Any, Dict
def presales_state_key(session_id: str) -> str:
    sid = session_id or "default"
    return f"presales_state:{sid}"


def load_presales_state(db: Any, *, session_id: str) -> Dict[str, Any]:
    if db is None:
        return {}
    key = presales_state_key(session_id)
    try:
        raw = db.get_meta(key)
    except Exception:
        raw = None
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_presales_state(db: Any, *, session_id: str, state: Dict[str, Any]) -> None:
    if db is None:
        return
    key = presales_state_key(session_id)
    payload = json.dumps(state or {}, ensure_ascii=False)
    try:
        db.set_meta(key, payload)
    except Exception:
        # Fail-open: confirmation isn't critical for non-SQLite environments.
        pass
#2027-05-04-zty-end
