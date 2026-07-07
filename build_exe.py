"""
Build a standalone Windows .exe for handing to a customer — no Python
required on their machine.

Usage:
    pip install -e ".[dev]"
    python build_exe.py

Output: dist/ACRA-Helper.exe
Ship it together with the companies/ folder (see dist_readme.txt).
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main() -> int:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ACRA-Helper",
        "--onefile",
        "--noconsole",
        "--clean",
        "--add-data", f"{BASE / 'web' / 'templates'};templates",
        "--add-data", f"{BASE / 'src' / 'acra_helper' / 'taxonomy' / 'calc_rules.json'};acra_helper/taxonomy",
        "--add-data", f"{BASE / 'src' / 'acra_helper' / 'taxonomy' / 'contexts_seed.json'};acra_helper/taxonomy",
        "--add-data", f"{BASE / 'src' / 'acra_helper' / 'taxonomy' / 'fact_map_seed.json'};acra_helper/taxonomy",
        "--paths", str(BASE / "src"),
        str(BASE / "web" / "app.py"),
    ]
    result = subprocess.run(cmd, cwd=BASE)
    if result.returncode == 0:
        print(f"\nBuilt: {BASE / 'dist' / 'ACRA-Helper.exe'}")
        print("Copy dist/ACRA-Helper.exe next to the companies/ folder before sharing.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
