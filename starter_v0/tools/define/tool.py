from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def define_word(word: str = "") -> dict[str, Any]:
    try:
        resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=15)
        if resp.status_code == 404:
            return {"tool": "define_word", "word": word, "items": []}
        resp.raise_for_status()
        data = resp.json()
        items = []
        for entry in data:
            meanings = entry.get("meanings", [])
            for m in meanings:
                for d in m.get("definitions", [])[:3]:
                    items.append({
                        "word": word,
                        "part_of_speech": m.get("partOfSpeech", ""),
                        "definition": d.get("definition", ""),
                        "example": d.get("example", ""),
                        "source": "dictionaryapi.dev",
                    })
        return {"tool": "define_word", "word": word, "items": items}
    except Exception as exc:
        return err("define_word", exc)
