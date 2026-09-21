#!/usr/bin/env python3
"""For each local task, report max TF-IDF similarity to any other task."""

from __future__ import annotations

import importlib.util
import sys
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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def main() -> int:
    tasks_dir = REPO_ROOT / "tasks"
    documents = load_task_documents(tasks_dir, include_structure_signals=True)
    task_ids = sorted(documents.keys())
    if len(task_ids) < 2:
        print("Need at least 2 tasks with instruction.md")
        return 1

    corpus = [documents[tid] for tid in task_ids]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000,
        lowercase=True,
        strip_accents="unicode",
    )
    matrix = vectorizer.fit_transform(corpus)
    sim = cosine_similarity(matrix)

    results: list[tuple[str, float, str]] = []
    for i, tid in enumerate(task_ids):
        row = sim[i].copy()
        row[i] = -1.0
        j = int(row.argmax())
        results.append((tid, float(row[j]), task_ids[j]))

    results.sort(key=lambda x: x[1])

    print(f"Tasks analyzed: {len(task_ids)} (include_structure=True)\n")
    print("10 tasks with LOWEST max-similarity (most unique):")
    print(f"{'rank':<5} {'task':<45} {'max_sim':>8}  nearest_neighbor")
    print("-" * 95)
    for rank, (tid, max_sim, neighbor) in enumerate(results[:10], start=1):
        print(f"{rank:<5} {tid:<45} {max_sim:8.4f}  {neighbor}")

    watch = ["hex-ko-vote-tally", "ical-recurrence-normalizer-052"]
    print("\nRequested tasks:")
    by_name = {tid: (max_sim, neighbor) for tid, max_sim, neighbor in results}
    for name in watch:
        if name not in by_name:
            print(f"  {name}: NOT FOUND")
            continue
        max_sim, neighbor = by_name[name]
        print(f"  {name}: max_sim={max_sim:.4f} (nearest: {neighbor})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
