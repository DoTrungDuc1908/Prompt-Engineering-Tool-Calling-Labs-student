from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_eval import load_cases, validate_expected_tools
from tools import TOOL_FUNCTIONS, load_tool_declarations


def validate_python() -> None:
    paths = [
        path
        for path in sorted(ROOT.rglob("*.py"))
        if ".venv" not in path.parts
    ]
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"Python syntax: {len(paths)} files")


def load_tool_docs() -> dict[str, dict[str, Any]]:
    docs: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "tools").glob("*/TOOL.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n"):
            raise ValueError(f"Missing TOOL.md frontmatter: {path}")
        _, frontmatter, _ = raw.split("---", 2)
        meta = yaml.safe_load(frontmatter)
        docs[meta["name"]] = meta
    return docs


def validate_tools() -> None:
    declarations = load_tool_declarations(ROOT / "artifacts" / "tools.yaml")
    declared = {item["name"] for item in declarations}
    implemented = set(TOOL_FUNCTIONS)
    documented = set(load_tool_docs())
    if declared != implemented or declared != documented:
        raise ValueError({
            "declared_without_registry": sorted(declared - implemented),
            "registry_without_declaration": sorted(implemented - declared),
            "declared_without_doc": sorted(declared - documented),
            "doc_without_declaration": sorted(documented - declared),
        })
    print(f"Tool contracts: {len(declared)} tools")


def validate_datasets() -> None:
    declarations = load_tool_declarations(ROOT / "artifacts" / "tools.yaml")
    for path in sorted((ROOT / "data").glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        cases = load_cases(path, "B")
        validate_expected_tools(cases, declarations, path)
        multiturn = sum("turns" in case for case in cases)
        print(f"{path.name}: {len(cases)} cases ({len(cases) - multiturn} single, {multiturn} multi)")

    group_cases = load_cases(ROOT / "data" / "eval_group.json", "B")
    group_multiturn = sum("turns" in case for case in group_cases)
    if len(group_cases) != 10 or group_multiturn != 5:
        raise ValueError("eval_group.json must contain exactly 10 cases: 5 single-turn and 5 multi-turn")


def main() -> None:
    validate_python()
    validate_tools()
    validate_datasets()
    print("Static validation passed.")


if __name__ == "__main__":
    main()
