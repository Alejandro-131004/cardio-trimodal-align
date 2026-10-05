"""Reorganize the DatasetCHVNGE folder (run once).

Moves, inside the dataset root:
  - numeric patient folders (new app, IDs 109+)       -> New_app_patients/
  - loose Rijuven .raw (ECG) and .mp3 (PCG) files     -> Rijuven_patients/
  - DB MultiScope spreadsheets (every version)        -> DB_Multiscope/
  - DB MultiScope copies inside patient folders       -> DB_Multiscope/ (renamed 'from_<ID>_<name>')
  - Patients_MultiScope spreadsheet                   -> Patients_Multiscope/
  - README files                                      -> README/
  - loose new app CSVs identical to a file that is
    already inside a patient folder (e.g. P135)       -> Duplicates/

Everything else (ECGs/, 12-lead folders, ...) is left untouched.
Running it again does nothing, because there are no files left to move.

Usage:
    python scripts/organize_data.py             # move the files
    python scripts/organize_data.py --dry-run   # only print what would be moved
"""

import argparse
import filecmp
import re
import shutil
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "data" / "DatasetCHVNGE"

NEW_APP_DIR = "New_app_patients"
RIJUVEN_DIR = "Rijuven_patients"
DB_DIR = "DB_Multiscope"
PATIENTS_DIR = "Patients_Multiscope"
README_DIR = "README"
DUPLICATES_DIR = "Duplicates"

RIJUVEN_RE = re.compile(r"^\d+_.+\.(raw|mp3)$", re.IGNORECASE)        # e.g. 1_AV.raw, 10_PV2.mp3
DB_RE = re.compile(r"DB[ _]?MultiScope", re.IGNORECASE)               # every DB MultiScope version
PATIENTS_RE = re.compile(r"^Patients_MultiScope", re.IGNORECASE)
NEW_APP_CSV_RE = re.compile(r"_(ECG|PCG|STE)_.+\.csv$", re.IGNORECASE)
EXCEL_EXTS = {".xlsx", ".xls", ".xlsm"}


def is_db_file(path: Path) -> bool:
    return path.suffix.lower() in EXCEL_EXTS and DB_RE.search(path.name) is not None


def find_folder_copy(path: Path, root: Path) -> Path | None:
    """Return an identical copy of a loose CSV that lives inside a patient folder, if any."""
    for other in root.rglob(path.name):
        if other != path and filecmp.cmp(path, other, shallow=False):
            return other
    return None


def destination(path: Path, root: Path) -> Path | None:
    """Folder where a top-level item belongs, or None to leave it where it is."""
    name = path.name
    if path.is_dir():
        return root / NEW_APP_DIR if name.isdigit() else None
    if name.startswith("~$"):  # Office lock file
        return None
    if RIJUVEN_RE.match(name):
        return root / RIJUVEN_DIR
    if "readme" in name.lower():
        return root / README_DIR
    if path.suffix.lower() in EXCEL_EXTS and PATIENTS_RE.match(name):
        return root / PATIENTS_DIR
    if is_db_file(path):
        return root / DB_DIR
    if NEW_APP_CSV_RE.search(name) and find_folder_copy(path, root):
        return root / DUPLICATES_DIR
    return None


def plan_moves(root: Path) -> tuple[list[tuple[Path, Path]], list[str]]:
    """List of (source, target) moves, plus the names of the top-level items left in place."""
    moves, left = [], []

    # DB copies inside patient folders (before or after the folders are moved)
    patient_dirs = [p for p in root.iterdir() if p.is_dir() and p.name.isdigit()]
    if (root / NEW_APP_DIR).is_dir():
        patient_dirs += [p for p in (root / NEW_APP_DIR).iterdir() if p.is_dir()]
    for folder in sorted(patient_dirs):
        for path in sorted(folder.iterdir()):
            if is_db_file(path) and not path.name.startswith("~$"):
                moves.append((path, root / DB_DIR / f"from_{folder.name}_{path.name}"))

    # Top-level items
    for path in sorted(root.iterdir()):
        target_dir = destination(path, root)
        if target_dir is None:
            left.append(path.name)
        else:
            moves.append((path, target_dir / path.name))
    return moves, left


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="dataset root folder")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without moving anything")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"Dataset root not found: {root}")

    moves, left = plan_moves(root)
    moved, skipped = Counter(), []
    for source, target in moves:
        if target.exists():
            skipped.append(source.name)
            continue
        if not args.dry_run:
            target.parent.mkdir(exist_ok=True)
            shutil.move(str(source), str(target))
        moved[target.parent.name] += 1

    mode = "Would move" if args.dry_run else "Moved"
    for folder, count in sorted(moved.items()):
        print(f"{mode} {count:4d} items -> {folder}/")
    if skipped:
        print(f"Skipped {len(skipped)} items (already exist at destination): {skipped}")
    print(f"Left in the root ({len(left)}): {left}")


if __name__ == "__main__":
    main()