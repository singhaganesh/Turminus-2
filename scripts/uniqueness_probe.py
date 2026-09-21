#!/usr/bin/env python3
"""Authoring uniqueness gate: occupancy + instruction + structure probes.

Failure modes this closes:
1. Invented similarity percentages (evidence law: quote Max similarity: only).
2. Spec public-contract clones while tasks/ is sparse.
3. Instruction-unique but structure-cloned tasks (same Go cmd/driver/stages
   house layout → ~78% with --include-structure while instruction-only is ~9%).

Commands:
  inventory       — occupied instruction heads + structure fingerprints
  probe           — TF-IDF draft instruction vs tasks/ + specs/
  structure       — TF-IDF finished/partial task dir with structure signals
  structure-plan  — TF-IDF planned layout before full tree exists

Max similarity 15%. Target ≤ 10%.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_CHECKS = REPO_ROOT / "ci_checks"
sys.path.insert(0, str(CI_CHECKS))

_spec = importlib.util.spec_from_file_location(
    "check_similarity", CI_CHECKS / "check-similarity.py"
)
_check_similarity = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_check_similarity)

load_task_documents = _check_similarity.load_task_documents
check_similarity = _check_similarity.check_similarity
SIMILARITY_ALERT_THRESHOLD = _check_similarity.SIMILARITY_ALERT_THRESHOLD
SIMILARITY_STRICT_TARGET = _check_similarity.SIMILARITY_STRICT_TARGET

from rubric_review import (  # noqa: E402
    build_similarity_document,
    extract_task_metadata,
    iter_visible_file_names,
    task_has_instruction_surface,
)

SPEC_SKIP_SUFFIXES = ("-validation-log.md",)
OUTPUT_PATH_RE = re.compile(r"/app/(?:output|out|var|store|prefix|bin)/[^\s,;`\"']+")
HEAD_WIDTH = 90

# Recurring house-layout families. Occupying one means the next task must not
# reuse the same family unless instruction+structure both stay ≤15%.
LAYOUT_FAMILIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("go-cmd-driver-stages", ("environment/cmd/driver/main.go", "environment/cmd/driver/stages/")),
    ("go-cmd-driver", ("environment/cmd/driver/main.go",)),
    ("rust-cargo-workspace", ("environment/Cargo.toml", "environment/src/")),
    ("c-make-prefix-mill", ("environment/CMakeLists.txt",)),
    ("python-pkg-under-environment", ("environment/pyproject.toml",)),
    ("node-package-json", ("environment/package.json",)),
)


@dataclass
class OccupiedItem:
    source: str  # "task" or "spec"
    name: str
    category: str
    languages: str
    tags: str
    head: str
    outputs: str
    document: str
    layout_family: str = ""
    env_roots: str = ""
    structure_document: str = ""
    structure_paths: list[str] = field(default_factory=list)


def _one_line(text: str, width: int = HEAD_WIDTH) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= width:
        return collapsed
    return collapsed[: width - 1] + "…"


def _meta_value(text: str, field: str) -> str:
    match = re.search(
        rf"^-\s*{re.escape(field)}:\s*(.+)$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if not match:
        return ""
    return match.group(1).strip().strip("`")


def _public_contract(text: str) -> str:
    match = re.search(
        r"^### Public contract\s*\n(.*?)(?=^### |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return ""
    return match.group(1).strip()


def _outputs(text: str) -> str:
    found = sorted(set(OUTPUT_PATH_RE.findall(text)))
    return ", ".join(found[:6])


def _parse_toml_metadata(toml: str) -> tuple[str, str, str]:
    category = languages = tags = ""
    in_metadata = False
    for raw in toml.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("[") and line.endswith("]"):
            in_metadata = line == "[metadata]"
            continue
        if not in_metadata or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key == "category":
            category = value.strip().strip('"').strip("'")
        elif key == "languages":
            languages = value
        elif key == "tags":
            tags = value
    return category, languages, tags


def detect_layout_family(paths: list[str]) -> str:
    joined = "\n".join(paths)
    hits: list[str] = []
    for family, markers in LAYOUT_FAMILIES:
        if all(marker in joined for marker in markers):
            hits.append(family)
    return ",".join(hits) if hits else "custom"


def env_root_summary(task_dir: Path) -> str:
    env = task_dir / "environment"
    if not env.is_dir():
        return ""
    roots: list[str] = []
    for child in sorted(env.iterdir()):
        if child.name.startswith("."):
            continue
        if child.name in {"Dockerfile", "docker-compose.yaml", "docker-compose.yml"}:
            continue
        roots.append(child.name + ("/" if child.is_dir() else ""))
    return ",".join(roots[:12])


def structure_document_from_paths(
    *,
    instruction: str,
    metadata: dict[str, str],
    paths: list[str],
    test_names: list[str] | None = None,
) -> str:
    lines = ["Instruction", instruction.strip() or "(structure-plan draft)"]
    if metadata:
        lines.append("")
        lines.append("Task metadata")
        for key in (
            "difficulty",
            "category",
            "codebase_size",
            "languages",
            "tags",
            "subcategories",
            "number_of_milestones",
        ):
            value = metadata.get(key)
            if value:
                lines.append(f"{key}: {value}")
    if paths:
        lines.append("")
        lines.append("Visible files")
        env_signals: list[str] = []
        for rel in paths:
            # Mirror build_similarity_document: drop Harbor boilerplate and the
            # shared environment/ prefix so structure-plan matches finished dirs.
            if rel in {
                "instruction.md",
                "task.toml",
                "rubric.txt",
                "output_contract.toml",
                "construction_manifest.json",
                "solution/solve.sh",
                "tests/test.sh",
                "tests/test_outputs.py",
                "environment/Dockerfile",
                "environment/.dockerignore",
                "environment/docker-compose.yaml",
                "environment/docker-compose.yml",
            }:
                continue
            signal = (
                rel[len("environment/") :]
                if rel.startswith("environment/")
                else rel
            )
            if signal in {"Dockerfile", ".dockerignore"}:
                continue
            env_signals.append(signal)
            norm = re.sub(r"[^a-z0-9]+", " ", signal.lower()).strip()
            lines.append(f"{signal} | {norm}")
            parts = signal.split("/")
            for depth in range(1, len(parts)):
                prefix = "/".join(parts[:depth]) + "/"
                pnorm = re.sub(r"[^a-z0-9]+", " ", prefix.lower()).strip()
                lines.append(f"{prefix} | {pnorm}")
        # Align with rubric_review.detect_layout_family_from_signals markers.
        joined = "\n".join(env_signals)
        family_hits: list[str] = []
        for family, markers in (
            ("go-cmd-driver-stages", ("cmd/driver/main.go", "cmd/driver/stages/")),
            ("go-cmd-driver", ("cmd/driver/main.go",)),
            ("rust-cargo-workspace", ("Cargo.toml", "src/")),
            ("c-make-prefix-mill", ("CMakeLists.txt",)),
            ("python-pkg-under-environment", ("pyproject.toml",)),
            ("node-package-json", ("package.json",)),
        ):
            if all(marker in joined for marker in markers):
                family_hits.append(family)
        lines.append("")
        lines.append("Layout family")
        lines.append(",".join(family_hits) if family_hits else "custom")
    if test_names:
        lines.append("")
        lines.append("Test names")
        for name in test_names:
            func = name.split("::")[-1]
            norm = re.sub(r"[^a-z0-9]+", " ", func.lower()).strip()
            lines.append(f"{func} | {norm}")
    return "\n".join(lines)


def load_task_items(tasks_dir: Path) -> list[OccupiedItem]:
    items: list[OccupiedItem] = []
    if not tasks_dir.exists():
        return items
    documents = load_task_documents(tasks_dir, include_structure_signals=False)
    for name, document in sorted(documents.items()):
        task_dir = tasks_dir / name
        toml = ""
        toml_path = task_dir / "task.toml"
        if toml_path.exists():
            toml = toml_path.read_text(encoding="utf-8", errors="replace")
        category, languages, tags = _parse_toml_metadata(toml)
        paths = iter_visible_file_names(task_dir)
        structure_doc = ""
        if task_has_instruction_surface(task_dir):
            structure_doc = build_similarity_document(
                task_dir, include_structure_signals=True
            ).strip()
        items.append(
            OccupiedItem(
                source="task",
                name=name,
                category=category,
                languages=languages,
                tags=tags,
                head=_one_line(document),
                outputs=_outputs(document),
                document=document,
                layout_family=detect_layout_family(paths),
                env_roots=env_root_summary(task_dir),
                structure_document=structure_doc,
                structure_paths=paths,
            )
        )
    return items


def load_spec_items(specs_dir: Path) -> list[OccupiedItem]:
    items: list[OccupiedItem] = []
    if not specs_dir.exists():
        return items
    for path in sorted(specs_dir.glob("*.md")):
        if path.name.endswith(SPEC_SKIP_SUFFIXES):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        contract = _public_contract(text)
        if not contract:
            continue
        name = _meta_value(text, "Task name") or path.stem
        # Spec Initial Draft Commitments / task_files paths if present
        paths = re.findall(
            r"^-\s*path:\s*(environment/[^\s]+|tests/[^\s]+|solution/[^\s]+)",
            text,
            re.MULTILINE,
        )
        languages = _meta_value(text, "Languages")
        category = _meta_value(text, "Category")
        meta = {
            "category": f'"{category}"' if category else "",
            "languages": languages,
            "difficulty": '"hard"',
        }
        structure_doc = structure_document_from_paths(
            instruction=contract,
            metadata={k: v for k, v in meta.items() if v},
            paths=paths,
        )
        items.append(
            OccupiedItem(
                source="spec",
                name=name,
                category=category,
                languages=languages,
                tags=_meta_value(text, "Tags"),
                head=_one_line(contract),
                outputs=_outputs(contract),
                document=contract,
                layout_family=detect_layout_family(paths) if paths else "unknown",
                env_roots=",".join(
                    sorted(
                        {
                            p.split("/")[1] + "/"
                            for p in paths
                            if p.startswith("environment/") and "/" in p[len("environment/") :]
                        }
                    )[:12]
                ),
                structure_document=structure_doc if paths else "",
                structure_paths=paths,
            )
        )
    return items


def format_inventory(
    tasks: list[OccupiedItem],
    specs: list[OccupiedItem],
    *,
    category: str | None = None,
    compact: bool = True,
) -> str:
    def keep(item: OccupiedItem) -> bool:
        return not category or item.category.lower() == category.lower()

    tasks = [item for item in tasks if keep(item)]
    specs = [item for item in specs if keep(item)]
    occupied_families = sorted(
        {item.layout_family for item in tasks if item.layout_family and item.layout_family != "custom"}
    )
    lines = [
        f"OCCUPIED tasks/: {len(tasks)}",
        f"OCCUPIED specs/ public-contract: {len(specs)}",
        "Gate: max 15% TF-IDF vs instruction AND structure; target ≤ 10%.",
        f"OCCUPIED layout families (do not reuse): {', '.join(occupied_families) or '(none named)'}",
        "",
    ]
    if compact:
        lines.append(
            "TASKS name | category | languages | layout_family | env_roots | outputs | instruction_head"
        )
        for item in tasks:
            lines.append(
                f"{item.name} | {item.category} | {item.languages} | "
                f"{item.layout_family} | {item.env_roots} | {item.outputs} | {item.head}"
            )
        lines.append("")
        lines.append(
            "SPECS name | category | languages | layout_family | env_roots | outputs | public_contract_head"
        )
        for item in specs:
            lines.append(
                f"{item.name} | {item.category} | {item.languages} | "
                f"{item.layout_family} | {item.env_roots} | {item.outputs} | {item.head}"
            )
        lines.append("")
        lines.append(
            "Structure rule: next task must change layout_family OR env_roots topology "
            "AND pass `structure` / `structure-plan` ≤15%. Same category+language+"
            "cmd/driver/stages house template is a known 78% failure mode."
        )
        return "\n".join(lines)

    for label, group in (("TASKS", tasks), ("SPECS", specs)):
        lines.append(f"== {label} ==")
        for item in group:
            lines.append(f"- {item.name}")
            lines.append(f"  category: {item.category}")
            lines.append(f"  languages: {item.languages}")
            lines.append(f"  tags: {item.tags}")
            lines.append(f"  layout_family: {item.layout_family}")
            lines.append(f"  env_roots: {item.env_roots}")
            lines.append(f"  outputs: {item.outputs}")
            lines.append(f"  head: {item.head}")
        lines.append("")
    return "\n".join(lines)


def _peer_documents(
    items: list[OccupiedItem],
    *,
    prefix: str,
    exclude: str | None,
    use_structure: bool = False,
) -> dict[str, str]:
    docs: dict[str, str] = {}
    for item in items:
        if exclude and item.name == exclude:
            continue
        text = item.structure_document if use_structure else item.document
        if not text or not text.strip():
            continue
        docs[f"{prefix}/{item.name}"] = text
    return docs


def _score_report(
    label: str,
    candidate: str,
    docs: dict[str, str],
    *,
    threshold: float,
) -> tuple[bool, int, str, list[str]]:
    lines: list[str] = []
    if not docs:
        lines.append(f"{label}: no peers, skip")
        return False, 0, "", lines
    max_sim, peer = check_similarity(candidate, docs)
    pct = int(max_sim * 100)
    lines.append(f"{label}: Max similarity: {pct}% with '{peer}'")
    failed = max_sim >= threshold
    if failed:
        lines.append(
            f"FAIL: {label} clone of '{peer}' "
            f"({pct}% >= {int(threshold * 100)}%). "
            "Redesign identity (domain, artifact, command, instruction voice, "
            "OR env topology / layout_family). Do not synonym-swap."
        )
    elif max_sim >= SIMILARITY_STRICT_TARGET:
        lines.append(
            f"WARN: {label} {pct}% is allowed but above the "
            f"{int(SIMILARITY_STRICT_TARGET * 100)}% target."
        )
    return failed, pct, peer, lines


def probe(
    instruction: str,
    tasks: list[OccupiedItem],
    specs: list[OccupiedItem],
    *,
    exclude: str | None = None,
    threshold: float = SIMILARITY_ALERT_THRESHOLD,
) -> tuple[int, str]:
    instruction = instruction.strip()
    if not instruction:
        return 1, "Error: draft instruction is empty"

    task_docs = _peer_documents(tasks, prefix="task", exclude=exclude)
    spec_docs = _peer_documents(specs, prefix="spec", exclude=exclude)
    lines = [
        "Uniqueness probe (instruction gate)",
        f"Threshold: {int(threshold * 100)}% max; target ≤ {int(SIMILARITY_STRICT_TARGET * 100)}%",
        f"Draft chars: {len(instruction)}",
        f"Peers: {len(task_docs)} tasks, {len(spec_docs)} specs",
        "NOTE: instruction pass ≠ structure pass. After skeleton exists, run "
        "`uniqueness_probe.py structure --task-dir tasks/<slug>`.",
    ]

    failed = False
    worst_pct = 0
    worst_peer = ""

    for label, docs in (("tasks/", task_docs), ("specs/", spec_docs)):
        bad, pct, peer, more = _score_report(
            label, instruction, docs, threshold=threshold
        )
        lines.extend(more)
        if pct > worst_pct:
            worst_pct, worst_peer = pct, peer
        failed = failed or bad

    if failed:
        lines.append(
            f"BLOCKED: worst {worst_pct}% vs {worst_peer}. "
            "Do not create remaining task files."
        )
        return 1, "\n".join(lines)

    if not task_docs and not spec_docs:
        lines.append("No peers found; uniqueness not proven against a corpus.")
        lines.append("Similarity within allowed band (empty peer set)")
        return 0, "\n".join(lines)

    lines.append(
        f"Max similarity: {worst_pct}% with '{worst_peer}' "
        f"(max allowed: {int(threshold * 100)}%; "
        f"target ≤ {int(SIMILARITY_STRICT_TARGET * 100)}%)"
    )
    lines.append("Similarity within allowed band")
    return 0, "\n".join(lines)


def structure_probe(
    candidate_doc: str,
    tasks: list[OccupiedItem],
    specs: list[OccupiedItem],
    *,
    exclude: str | None = None,
    threshold: float = SIMILARITY_ALERT_THRESHOLD,
    candidate_family: str = "",
) -> tuple[int, str]:
    if not candidate_doc.strip():
        return 1, "Error: structure document is empty"

    task_docs = _peer_documents(
        tasks, prefix="task", exclude=exclude, use_structure=True
    )
    # Specs only contribute when they declared concrete env paths.
    spec_docs = _peer_documents(
        specs, prefix="spec", exclude=exclude, use_structure=True
    )

    occupied = sorted(
        {
            item.layout_family
            for item in tasks
            if item.name != exclude
            and item.layout_family
            and item.layout_family not in {"", "custom", "unknown"}
        }
    )
    lines = [
        "Uniqueness probe (structure gate)",
        f"Threshold: {int(threshold * 100)}% max; target ≤ {int(SIMILARITY_STRICT_TARGET * 100)}%",
        f"Candidate layout_family: {candidate_family or 'custom'}",
        f"Occupied layout families: {', '.join(occupied) or '(none named)'}",
        f"Peers with structure docs: {len(task_docs)} tasks, {len(spec_docs)} specs",
    ]

    family_block = False
    if candidate_family and candidate_family not in {"custom", "unknown"}:
        for fam in candidate_family.split(","):
            if fam in occupied:
                family_block = True
                lines.append(
                    f"FAIL: layout_family '{fam}' already occupied. "
                    "Pick a different env topology (not the same cmd/driver/stages "
                    "or equivalent house skeleton)."
                )

    failed = family_block
    worst_pct = 0
    worst_peer = ""

    for label, docs in (("tasks+structure/", task_docs), ("specs+structure/", spec_docs)):
        bad, pct, peer, more = _score_report(
            label, candidate_doc, docs, threshold=threshold
        )
        lines.extend(more)
        if pct > worst_pct:
            worst_pct, worst_peer = pct, peer
        failed = failed or bad

    if failed:
        lines.append(
            f"BLOCKED: structure worst {worst_pct}% vs {worst_peer or 'layout_family'}. "
            "Tear down and redesign topology — do not rename modules in the same layout."
        )
        return 1, "\n".join(lines)

    if not task_docs and not spec_docs and not family_block:
        lines.append("No structured peers found; structure uniqueness not proven.")
        lines.append("Similarity within allowed band (empty peer set)")
        return 0, "\n".join(lines)

    lines.append(
        f"Max similarity: {worst_pct}% with '{worst_peer}' "
        f"(max allowed: {int(threshold * 100)}%; "
        f"target ≤ {int(SIMILARITY_STRICT_TARGET * 100)}%)"
    )
    lines.append("Similarity within allowed band")
    return 0, "\n".join(lines)


def parse_structure_manifest(path: Path) -> tuple[dict[str, str], list[str], list[str]]:
    """Parse a simple structure plan.

    Format:
      category: debugging
      languages: ["go"]
      tags: ["a", "b"]
      difficulty: hard
      codebase_size: small
      path: environment/foo/bar.go
      path: tests/test_outputs.py
      test: test_foo
    """
    metadata: dict[str, str] = {}
    paths: list[str] = []
    tests: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key_l = key.lower()
        if key_l == "path":
            paths.append(value)
        elif key_l == "test":
            tests.append(value)
        elif key_l in {
            "category",
            "languages",
            "tags",
            "difficulty",
            "codebase_size",
            "subcategories",
            "number_of_milestones",
        }:
            if key_l in {"category", "difficulty", "codebase_size"} and not value.startswith(
                '"'
            ):
                metadata[key_l] = f'"{value}"'
            else:
                metadata[key_l] = value
    return metadata, paths, tests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Occupancy inventory + instruction/structure uniqueness probes (max 15%).",
    )
    parser.add_argument(
        "command",
        choices=("inventory", "probe", "structure", "structure-plan"),
        help=(
            "inventory | probe (instruction) | structure (task dir) | "
            "structure-plan (manifest before full tree)"
        ),
    )
    parser.add_argument("--instruction", type=Path, help="Draft instruction.md (probe)")
    parser.add_argument(
        "--task-dir",
        type=Path,
        help="Partial/finished task directory (structure)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Structure plan file for structure-plan",
    )
    parser.add_argument("--exclude", help="Own slug to exclude from peers")
    parser.add_argument("--category", help="Filter inventory to one primary category")
    parser.add_argument("--tasks-dir", type=Path, default=REPO_ROOT / "tasks")
    parser.add_argument("--specs-dir", type=Path, default=REPO_ROOT / "specs")
    parser.add_argument("--threshold", type=float, default=SIMILARITY_ALERT_THRESHOLD)
    parser.add_argument(
        "--full",
        action="store_true",
        help="Inventory: verbose fingerprints",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0.0 <= args.threshold <= 1.0:
        print(f"Error: --threshold must be between 0 and 1, got {args.threshold}")
        return 1

    tasks = load_task_items(args.tasks_dir)
    specs = load_spec_items(args.specs_dir)

    if args.command == "inventory":
        print(
            format_inventory(
                tasks,
                specs,
                category=args.category,
                compact=not args.full,
            )
        )
        return 0

    if args.command == "probe":
        if args.instruction is None:
            print("Error: probe requires --instruction PATH")
            return 1
        if not args.instruction.is_file():
            print(f"Error: instruction file not found: {args.instruction}")
            return 1
        text = args.instruction.read_text(encoding="utf-8")
        code, report = probe(
            text,
            tasks,
            specs,
            exclude=args.exclude,
            threshold=args.threshold,
        )
        print(report)
        return code

    if args.command == "structure":
        if args.task_dir is None:
            print("Error: structure requires --task-dir tasks/<slug>")
            return 1
        if not args.task_dir.is_dir():
            print(f"Error: task dir not found: {args.task_dir}")
            return 1
        if not task_has_instruction_surface(args.task_dir):
            print(f"Error: no instruction surface under {args.task_dir}")
            return 1
        exclude = args.exclude or args.task_dir.name
        doc = build_similarity_document(
            args.task_dir, include_structure_signals=True
        ).strip()
        paths = iter_visible_file_names(args.task_dir)
        family = detect_layout_family(paths)
        code, report = structure_probe(
            doc,
            tasks,
            specs,
            exclude=exclude,
            threshold=args.threshold,
            candidate_family=family,
        )
        print(report)
        return code

    # structure-plan
    if args.manifest is None:
        print("Error: structure-plan requires --manifest PATH")
        return 1
    if not args.manifest.is_file():
        print(f"Error: manifest not found: {args.manifest}")
        return 1
    metadata, paths, test_names = parse_structure_manifest(args.manifest)
    if len(paths) < 5:
        print(
            "Error: structure-plan manifest needs ≥5 path: lines "
            "(planned environment/tests files, not only Harbor boilerplate)"
        )
        return 1
    instruction = ""
    if args.instruction and args.instruction.is_file():
        instruction = args.instruction.read_text(encoding="utf-8")
    doc = structure_document_from_paths(
        instruction=instruction,
        metadata=metadata,
        paths=paths,
        test_names=test_names,
    )
    family = detect_layout_family(paths)
    code, report = structure_probe(
        doc,
        tasks,
        specs,
        exclude=args.exclude,
        threshold=args.threshold,
        candidate_family=family,
    )
    print(report)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
