from __future__ import annotations

from typing import Any

from tools._shared import err


def calculate(expression: str = "") -> dict[str, Any]:
    try:
        import sympy
        normalized = expression.replace("^", "**")
        parsed = sympy.sympify(normalized)
        result = sympy.N(parsed) if parsed.is_number else parsed
        return {"tool": "calculate", "expression": expression, "items": [{
            "expression": expression,
            "result": str(result),
            "simplified": str(sympy.simplify(parsed)) if parsed != result else None,
        }]}
    except Exception as exc:
        return err("calculate", exc)


def calculate_safe(expression: str) -> dict[str, Any]:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"tool": "calculate", "expression": expression, "items": [{
            "expression": expression,
            "result": str(result),
        }]}
    except Exception as exc:
        return err("calculate", exc)
