"""Verifier for ship mill watch.json and peek stdout."""

from __future__ import annotations

import io
import json
import subprocess
import zipfile
from pathlib import Path

WATCH = Path("/app/jarhearth/watch.json")
JAR = Path("/app/jarhearth/ship.jar")
ALPHA = Path("/app/hopbags/alpha.bag")
ELM = Path("/app/hopbags/elm.bag")
MUTE = Path("/app/hopbags/mute.bag")
MARK = Path("/app/opslip/MARK.txt")

_PROBE = """public class CinderProbe {
    public static void main(String[] a) throws Exception {
        int w = Integer.parseInt(a[0]);
        Tarn t = new Tarn();
        System.out.println(Glue.haul(t, w));
    }
}
"""

_BOARD: dict[int, int] = {}


def _token(bag: Path) -> int:
    return int(bag.read_text().splitlines()[0].strip())


def _board(token: int) -> int:
    if token in _BOARD:
        return _BOARD[token]
    tmp = Path("/tmp/cinderprobe")
    tmp.mkdir(parents=True, exist_ok=True)
    src = tmp / "CinderProbe.java"
    src.write_text(_PROBE)
    jdk = Path("/opt/java/openjdk/bin")
    javac = jdk / "javac"
    java = jdk / "java"
    if not javac.is_file():
        javac = Path("/usr/bin/javac")
        java = Path("/usr/bin/java")
    c1 = subprocess.run(
        [javac, "-cp", JAR, "-d", tmp, src],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert c1.returncode == 0, c1.stderr
    c2 = subprocess.run(
        [java, "-cp", f"{tmp.as_posix()}:{JAR.as_posix()}", "CinderProbe", str(token)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert c2.returncode == 0, c2.stderr
    got = int(c2.stdout.strip())
    _BOARD[token] = got
    return got


def _word(bag: Path) -> int:
    token = _token(bag)
    if token == 0:
        return 0
    got = _board(token)
    assert got != 0
    assert got != token
    return got


def _watch(bag: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/cinderwait", "watch", bag.as_posix()],
        capture_output=True,
        text=True,
    )


def _peek(bag: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/cinderwait", "peek", bag.as_posix()],
        capture_output=True,
        text=True,
    )


def _obj() -> dict:
    return json.loads(WATCH.read_text())


def test_cw01_oak_hit():
    """Ship watch of alpha.bag stores that bag's gather word."""
    r = _watch(ALPHA)
    assert r.returncode == 0, r.stderr
    obj = _obj()
    assert obj["seen"] == _word(ALPHA)
    assert obj["seen"] != _token(ALPHA)
    assert obj["bag"] == "alpha.bag"


def test_cw02_elm_hit():
    """Ship watch of elm.bag stores that bag's gather word."""
    r = _watch(ELM)
    assert r.returncode == 0, r.stderr
    obj = _obj()
    assert obj["seen"] == _word(ELM)
    assert obj["seen"] != _token(ELM)


def test_cw03_ash_hit():
    """peek of alpha.bag prints the gather word."""
    r = _peek(ALPHA)
    assert r.returncode == 0, r.stderr
    assert int(r.stdout.strip()) == _word(ALPHA)
    assert int(r.stdout.strip()) != _token(ALPHA)


def test_cw04_seal_jar():
    """watch exits non-zero when the MARK.txt stamp is missing from ship.jar."""
    orig = JAR.read_bytes()
    try:
        buf = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(orig), "r") as zin, zipfile.ZipFile(buf, "w") as zout:
            for info in zin.infolist():
                if info.filename == "STAMP":
                    continue
                zout.writestr(info, zin.read(info.filename))
        JAR.write_bytes(buf.getvalue())
        r = _watch(ALPHA)
        assert r.returncode != 0
    finally:
        JAR.write_bytes(orig)


def test_cw05_mute_rc():
    """watch of a never-published bag exits non-zero."""
    r = _watch(MUTE)
    assert r.returncode != 0


def test_cw06_mute_vat():
    """watch of a never-published bag does not leave success watch.json."""
    if WATCH.is_file():
        WATCH.unlink()
    r = _watch(MUTE)
    assert r.returncode != 0
    assert not WATCH.is_file()


def test_cw07_held_hit():
    """Held-out published bag still stores its gather word."""
    p = Path("/app/hopbags/held.bag")
    p.write_text("8181\n")
    r = _watch(p)
    assert r.returncode == 0, r.stderr
    obj = _obj()
    assert obj["seen"] == _word(p)
    assert obj["seen"] != 8181


def test_cw08_held_list():
    """peek of a held-out bag prints its gather word."""
    p = Path("/app/hopbags/held2.bag")
    p.write_text("9191\n")
    r = _peek(p)
    assert r.returncode == 0, r.stderr
    assert int(r.stdout.strip()) == _word(p)
    assert int(r.stdout.strip()) != 9191


def test_cw09_elm_list():
    """peek of elm.bag prints the gather word."""
    r = _peek(ELM)
    assert r.returncode == 0, r.stderr
    assert int(r.stdout.strip()) == _word(ELM)
    assert int(r.stdout.strip()) != _token(ELM)


def test_cw10_seal_rc():
    """watch exits non-zero when MARK.txt is absent."""
    orig = MARK.read_text()
    try:
        MARK.unlink()
        r = _watch(ALPHA)
        assert r.returncode != 0
    finally:
        MARK.write_text(orig)


def test_cw11_corrupt_vat():
    """Corrupt watch.json then rerun watch; ship mill restores the gather word."""
    WATCH.parent.mkdir(parents=True, exist_ok=True)
    WATCH.write_text("{\"seen\":0,\"bag\":\"x\",\"note\":\"x\"}\n")
    r = _watch(ALPHA)
    assert r.returncode == 0, r.stderr
    obj = _obj()
    assert obj["seen"] == _word(ALPHA)
    assert obj["seen"] != _token(ALPHA)


def test_cw12_side_hit():
    """peek of a grade-time bag prints its gather word."""
    p = Path("/app/hopbags/side.bag")
    p.write_text("6060\n")
    r = _peek(p)
    assert r.returncode == 0, r.stderr
    assert int(r.stdout.strip()) == _word(p)
    assert int(r.stdout.strip()) != 6060
