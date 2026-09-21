from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE = REPO_ROOT / "scripts" / "uniqueness_probe.py"


CLONE_CONTRACT = (
    "Repair C sources under `/app/environment` so `/app/bin/rewire refresh` "
    "re-pins crates from `/app/environment/bins`, replaces `/app/var/hop.lock` "
    "with one rename, materializes `/app/store`, and writes `/app/output/shift.json`. "
    "Hand-placed store files or JSON are not enough."
)
FRESH_INSTRUCTION = (
    "Count lunar basalt vesicles from a Fortran namelist under "
    "/opt/mare/crater.f90 and write /var/lib/vesicle/tally.nml "
    "with isotope bins only."
)


class UniquenessProbeTest(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PROBE), *args],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

    def _corpus(self, tmp: Path) -> tuple[Path, Path]:
        tasks = tmp / "tasks"
        specs = tmp / "specs"
        tasks.mkdir()
        specs.mkdir()
        (specs / "silo-crate-rewire.md").write_text(
            "### Metadata\n"
            "- Task name: silo-crate-rewire\n"
            "- Category: debugging\n"
            "- Languages: [c]\n"
            "- Tags: [hop-lock]\n\n"
            "## Authoring Brief\n\n"
            "### Public contract\n"
            f"{CLONE_CONTRACT}\n\n"
            "### platform_files\n"
            "- path: task.toml\n"
            "- path: environment/cmd/driver/main.go\n"
            "- path: environment/cmd/driver/stages/run.go\n",
            encoding="utf-8",
        )
        return tasks, specs

    def _write_go_driver_task(self, tasks_dir: Path, name: str, instruction: str) -> Path:
        task = tasks_dir / name
        (task / "environment" / "cmd" / "driver" / "stages").mkdir(parents=True)
        (task / "tests").mkdir(parents=True)
        (task / "solution").mkdir(parents=True)
        (task / "instruction.md").write_text(instruction, encoding="utf-8")
        (task / "task.toml").write_text(
            """version = "2.0"

[metadata]
difficulty = "hard"
category = "build-and-dependency-management"
tags = ["go", "driver"]
languages = ["go"]
codebase_size = "small"
number_of_milestones = 0
subcategories = []
""",
            encoding="utf-8",
        )
        (task / "environment" / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        (task / "environment" / "go.mod").write_text("module example\n", encoding="utf-8")
        (task / "environment" / "cmd" / "driver" / "main.go").write_text(
            "package main\n", encoding="utf-8"
        )
        (task / "environment" / "cmd" / "driver" / "stages" / "run.go").write_text(
            "package stages\n", encoding="utf-8"
        )
        (task / "tests" / "test.sh").write_text("#!/bin/bash\n", encoding="utf-8")
        (task / "tests" / "test_outputs.py").write_text(
            "def test_report():\n    assert True\n", encoding="utf-8"
        )
        (task / "solution" / "solve.sh").write_text("#!/bin/bash\n", encoding="utf-8")
        return task

    def test_inventory_lists_layout_families(self) -> None:
        result = self._run("inventory")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OCCUPIED tasks/", result.stdout)
        self.assertIn("OCCUPIED layout families", result.stdout)
        self.assertIn("layout_family", result.stdout)

    def test_probe_blocks_spec_public_contract_clone(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            tasks, specs = self._corpus(tmp)
            draft = tmp / "clone.md"
            draft.write_text(CLONE_CONTRACT, encoding="utf-8")
            result = self._run(
                "probe",
                "--instruction",
                str(draft),
                "--exclude",
                "not-a-real-slug",
                "--tasks-dir",
                str(tasks),
                "--specs-dir",
                str(specs),
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("FAIL:", result.stdout)
            self.assertIn("specs/", result.stdout)
            self.assertRegex(result.stdout, r"Max similarity: \d+%")

    def test_probe_allows_unrelated_instruction(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            tasks, specs = self._corpus(tmp)
            draft = tmp / "fresh.md"
            draft.write_text(FRESH_INSTRUCTION, encoding="utf-8")
            result = self._run(
                "probe",
                "--instruction",
                str(draft),
                "--exclude",
                "lunar-vesicle-tally",
                "--tasks-dir",
                str(tasks),
                "--specs-dir",
                str(specs),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Similarity within allowed band", result.stdout)

    def test_structure_blocks_go_cmd_driver_clone(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            tasks = tmp / "tasks"
            specs = tmp / "specs"
            tasks.mkdir()
            specs.mkdir()
            self._write_go_driver_task(
                tasks,
                "peer-alpha",
                "Alpha peer plans forge units from a YAML focus field under /app.",
            )
            clone = self._write_go_driver_task(
                tasks,
                "peer-beta",
                "Beta peer culls shard blobs by age under /opt/vault with zone stamps.",
            )
            result = self._run(
                "structure",
                "--task-dir",
                str(clone),
                "--exclude",
                "peer-beta",
                "--tasks-dir",
                str(tasks),
                "--specs-dir",
                str(specs),
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("structure gate", result.stdout)
            self.assertTrue(
                "layout_family" in result.stdout or "FAIL:" in result.stdout,
                result.stdout,
            )

    def test_structure_plan_blocks_occupied_family(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            tasks = tmp / "tasks"
            specs = tmp / "specs"
            tasks.mkdir()
            specs.mkdir()
            self._write_go_driver_task(
                tasks,
                "peer-alpha",
                "Alpha peer plans forge units from a YAML focus field under /app.",
            )
            manifest = tmp / "plan.txt"
            manifest.write_text(
                "\n".join(
                    [
                        "category: build-and-dependency-management",
                        "languages: [\"go\"]",
                        "difficulty: hard",
                        "codebase_size: small",
                        "path: environment/cmd/driver/main.go",
                        "path: environment/cmd/driver/stages/cut.go",
                        "path: environment/go.mod",
                        "path: environment/docs/cli.md",
                        "path: environment/trim/cull.go",
                        "path: tests/test_outputs.py",
                        "test: test_report",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            result = self._run(
                "structure-plan",
                "--manifest",
                str(manifest),
                "--exclude",
                "new-task",
                "--tasks-dir",
                str(tasks),
                "--specs-dir",
                str(specs),
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("go-cmd-driver-stages", result.stdout)

    def test_probe_requires_instruction(self) -> None:
        result = self._run("probe")
        self.assertEqual(result.returncode, 1)
        self.assertIn("probe requires --instruction", result.stdout)


if __name__ == "__main__":
    unittest.main()
