from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

MEMORY_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "agent_memory.json"

def manage_memory(action: str = "list", key: str = "", value: str = "") -> dict[str, Any]:
    """Saves, loads, lists, or deletes entries in the agent's persistent local memory store."""
    try:
        # Ensure data folder exists
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
        else:
            memory = {}

        action = action.lower()
        if action == "save":
            if not key:
                return {"tool": "agent_memory", "status": "error", "error": "key is required to save memory."}
            memory[key] = {
                "value": value,
                "timestamp": memory.get(key, {}).get("timestamp", "") or str(Path(__file__).stat().st_mtime) # simple mock of datetime or basic metadata
            }
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=4, ensure_ascii=False)
            return {"tool": "agent_memory", "status": "success", "message": f"Successfully saved key '{key}' to memory."}

        elif action == "load":
            if not key:
                return {"tool": "agent_memory", "status": "error", "error": "key is required to load memory."}
            if key not in memory:
                return {"tool": "agent_memory", "status": "not_found", "message": f"Key '{key}' not found in memory."}
            return {"tool": "agent_memory", "status": "success", "key": key, "value": memory[key]["value"]}

        elif action == "delete":
            if not key:
                return {"tool": "agent_memory", "status": "error", "error": "key is required to delete."}
            if key in memory:
                del memory[key]
                with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(memory, f, indent=4, ensure_ascii=False)
                return {"tool": "agent_memory", "status": "success", "message": f"Deleted key '{key}' from memory."}
            return {"tool": "agent_memory", "status": "not_found", "message": f"Key '{key}' not found."}

        else: # "list"
            keys = list(memory.keys())
            return {"tool": "agent_memory", "status": "success", "keys": keys, "count": len(keys)}

    except Exception as e:
        return {"tool": "agent_memory", "status": "error", "error": str(e)}
