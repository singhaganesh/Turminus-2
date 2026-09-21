import zipfile
from pathlib import Path


def read_stamp(jar: Path) -> str:
    with zipfile.ZipFile(jar) as z:
        if "STAMP" not in z.namelist():
            return ""
        return z.read("STAMP").decode().strip()
