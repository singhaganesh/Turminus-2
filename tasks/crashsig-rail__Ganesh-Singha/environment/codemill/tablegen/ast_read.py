"""AST helpers for generated maps."""

from __future__ import annotations

import ast
from typing import Dict


def read_map_literal(text: str) -> Dict[str, str]:
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SIGNATURE_OWNERS":
                    raw = ast.literal_eval(node.value)
                    if not isinstance(raw, dict):
                        raise ValueError("not a dict")
                    return {str(k): str(v) for k, v in raw.items()}
    raise ValueError("SIGNATURE_OWNERS not found")
