from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SIMILARITY = REPO_ROOT / "ci_checks" / "check-similarity.py"


class CheckSimilarityPolicyTest(unittest.TestCase):
    def test_local_threshold_matches_platform_fifteen_percent(self) -> None:
        text = CHECK_SIMILARITY.read_text(encoding="utf-8")
        alert = re.search(
            r"^SIMILARITY_ALERT_THRESHOLD\s*=\s*([0-9.]+)",
            text,
            re.MULTILINE,
        )
        target = re.search(
            r"^SIMILARITY_STRICT_TARGET\s*=\s*([0-9.]+)",
            text,
            re.MULTILINE,
        )
        self.assertIsNotNone(alert)
        self.assertIsNotNone(target)
        self.assertAlmostEqual(float(alert.group(1)), 0.15)
        self.assertAlmostEqual(float(target.group(1)), 0.10)

    def test_check_similarity_script_documents_uniqueness_gate(self) -> None:
        text = CHECK_SIMILARITY.read_text(encoding="utf-8")
        self.assertIn("15%", text)
        self.assertIn("platform uniqueness gate", text)
        self.assertIn("--draft-instruction", text)

    def test_draft_instruction_scores_without_task_dir(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            draft = Path(raw) / "draft.md"
            draft.write_text(
                "Count lunar basalt vesicles from a Fortran namelist under "
                "/opt/mare/crater.f90 and write /var/lib/vesicle/tally.nml.",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_SIMILARITY),
                    "--draft-instruction",
                    str(draft),
                    "--enforce-threshold",
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Max similarity:", result.stdout)
            self.assertIn("draft instruction file", result.stdout)


if __name__ == "__main__":
    unittest.main()
