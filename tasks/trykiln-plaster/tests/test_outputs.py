"""Behavioral checks for kiln vats and kilncli assay/spill."""

from __future__ import annotations

import subprocess
from pathlib import Path

MIG = Path("/app/inkstack/migrations")
PLASTER = Path("/app/vats/plaster.vat")
WORKER = Path("/app/vats/worker.vat")
OK = Path("/app/vats/assay.ok")
CLI = "/app/bin/kilncli"

LAGGING = """KILNVAT 1
applied:0003_base
table:tries
cols:id,label
row:1,boot
"""


def parse_vat(path: Path) -> dict:
    applied = []
    cols: list[str] = []
    table = ""
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("applied:"):
            applied.append(line.split(":", 1)[1])
        elif line.startswith("table:"):
            table = line.split(":", 1)[1]
        elif line.startswith("cols:"):
            cols = line.split(":", 1)[1].split(",")
    return {"applied": applied, "cols": cols, "table": table}


def sql_head() -> str:
    stems = sorted(p.stem for p in MIG.glob("*.sql"))
    assert stems
    return stems[len(stems) - 1]


def last_applied(path: Path) -> str:
    final = ""
    for line in path.read_text().splitlines():
        if line.startswith("applied:"):
            final = line.split(":", 1)[1]
    return final


def test_k01_plaster_column():
    """Plaster vat final applied stem equals ledger sql head."""
    assert last_applied(PLASTER) == sql_head()


def test_k02_worker_column():
    """Worker vat final applied stem equals ledger sql head."""
    assert last_applied(WORKER) == sql_head()


def test_k03_applied_head():
    """Last applied stem on plaster equals ledger sql head."""
    assert last_applied(PLASTER) == sql_head()


def test_k04_column_parity():
    """Plaster and worker column lists match and both sit on the sql head."""
    a = parse_vat(PLASTER)
    b = parse_vat(WORKER)
    assert a["applied"] == b["applied"]
    assert last_applied(PLASTER) == sql_head()
    assert "attempt_slot" in a["cols"]
    assert "attempt_slot" in b["cols"]


def test_k05_lag_copy_exit():
    """Spill of a vat behind the sql head exits non-zero."""
    orig = PLASTER.read_text()
    worker_orig = WORKER.read_bytes()
    try:
        PLASTER.write_text(LAGGING)
        proc = subprocess.run([CLI, "spill"], capture_output=True, text=True)
        assert proc.returncode != 0
    finally:
        PLASTER.write_text(orig)
        WORKER.write_bytes(worker_orig)


def test_k06_lag_copy_untouched():
    """Failed lag spill leaves a marked worker vat unchanged."""
    orig = PLASTER.read_text()
    worker_orig = WORKER.read_text()
    marked = worker_orig.replace("row:1,boot", "row:9,marked")
    if marked == worker_orig:
        marked = worker_orig + "row:9,marked\n"
    try:
        WORKER.write_text(marked)
        PLASTER.write_text(LAGGING)
        subprocess.run([CLI, "spill"], capture_output=True, text=True)
        assert "marked" in WORKER.read_text()
    finally:
        PLASTER.write_text(orig)
        WORKER.write_text(worker_orig)


def test_k07_holdout_sql_head():
    """Extra unseen sql stem makes spill reject the current plaster."""
    extra = MIG / "0005_holdout.sql"
    orig_w = WORKER.read_bytes()
    try:
        extra.write_text("ALTER TABLE tries ADD COLUMN hold_pad;\n")
        proc = subprocess.run([CLI, "spill"], capture_output=True, text=True)
        assert proc.returncode != 0
    finally:
        extra.unlink(missing_ok=True)
        WORKER.write_bytes(orig_w)


def test_k08_zz_recover_worker():
    """Corrupt worker then spill recovers columns from plaster."""
    orig = WORKER.read_text()
    try:
        WORKER.write_text("KILNVAT 1\n")
        proc = subprocess.run([CLI, "spill"], capture_output=True, text=True)
        assert proc.returncode == 0
        assay = subprocess.run([CLI, "assay"], capture_output=True, text=True)
        assert assay.returncode == 0
        assert last_applied(WORKER) == sql_head()
    finally:
        if "attempt_slot" not in parse_vat(PLASTER)["cols"]:
            WORKER.write_text(orig)


def test_k09_ok_marker():
    """Successful assay writes assay.ok."""
    assert OK.is_file()
    assert "ok" in OK.read_text()


def test_k10_version_print():
    """Assay stdout prints schema_version equal to sql head."""
    proc = subprocess.run([CLI, "assay"], capture_output=True, text=True)
    assert proc.returncode == 0
    line = [ln for ln in proc.stdout.splitlines() if ln.startswith("schema_version=")]
    assert line
    assert line[0] == f"schema_version={sql_head()}"


def test_k11_version_matches_head():
    """Worker last applied independently matches ledger head."""
    assert last_applied(WORKER) == sql_head()


def test_k12_second_run():
    """Assay twice yields the same schema_version line."""
    a = subprocess.run([CLI, "assay"], capture_output=True, text=True)
    b = subprocess.run([CLI, "assay"], capture_output=True, text=True)
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout


def test_k13_clean_exit():
    """Assay exits zero on the repaired worker vat."""
    proc = subprocess.run([CLI, "assay"], capture_output=True, text=True)
    assert proc.returncode == 0
    assert OK.is_file()


def test_k14_lag_worker_refuses():
    """Assay refuses a worker that has the column but an old applied stem."""
    orig = WORKER.read_text()
    ok_orig = OK.read_bytes() if OK.is_file() else None
    try:
        WORKER.write_text(
            "KILNVAT 1\n"
            "applied:0003_base\n"
            "table:tries\n"
            "cols:id,label,attempt_slot\n"
            "row:1,boot,0\n"
        )
        if OK.is_file():
            OK.unlink()
        proc = subprocess.run([CLI, "assay"], capture_output=True, text=True)
        assert proc.returncode != 0
    finally:
        WORKER.write_text(orig)
        if ok_orig is not None:
            OK.write_bytes(ok_orig)
        else:
            subprocess.run([CLI, "assay"], capture_output=True, text=True)
