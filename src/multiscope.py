"""Shared code for the MultiScope notebooks: paths, helpers, signal readers and the recording index."""

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

# ---------------------------------------------------------------- Configuration

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "DatasetCHVNGE"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_FILE = OUTPUT_DIR / "reports_deidentified.pkl"   # de-identified echocardiography reports

NEW_APP_DIR = DATA_ROOT / "New_app_patients"
RIJUVEN_DIR = DATA_ROOT / "Rijuven_patients"
DB_DIR = DATA_ROOT / "DB_Multiscope"
QUALITY_DIR = DATA_ROOT / "Quality_Annotations"
NEW_12_LEAD_DIR = DATA_ROOT / "New_12_lead_ECG"
UNUSED_DIR = DATA_ROOT / "Unused"   # data the supervisor said to disregard

CLINICAL_DB_GLOB = "18.09.2026_DB MultiScope*.xlsx"   # clinical database used in the thesis
REPORT_COLUMN = "Report_ecoTT"                        # free-text echocardiography report

RIJUVEN_ECG_FS = 500    # not stored in the .raw files, value from the original script
RIJUVEN_MAX_ID = 108    # Rijuven files of later patients are ignored (they also have new app recordings)
NO_SIGNAL_IDS = [71, 72, 73, 74, 75, 76, 77, 131, 132, 273, 274, 275]   # no usable ECG/PCG

# Column names that identify a patient (compared in lowercase)
IDENTIFIER_NAMES = {"name", "nome", "nsc", "proc", "birthday", "data de nascimento"}

# Every valve spelling used by both apps, mapped to one code
SITE_MAP = {"av": "AV", "aortica": "AV", "mv": "MV", "mitral": "MV",
            "pv": "PV", "pulmonar": "PV", "tv": "TV", "tricuspide": "TV"}

# ---------------------------------------------------------------- Helpers


def drop_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the columns that identify a patient."""
    return df[[c for c in df.columns if str(c).strip().lower() not in IDENTIFIER_NAMES]]


def read_table(path: Path, **kwargs) -> pd.DataFrame:
    """Read a spreadsheet without its identifier columns."""
    return drop_identifiers(pd.read_excel(path, **kwargs))


def load_db_version(path: Path) -> pd.DataFrame:
    """One DB version without identifiers, one row per numeric ID."""
    df = read_table(path)
    df["ID"] = pd.to_numeric(df["ID"], errors="coerce")
    return df.dropna(subset=["ID"]).astype({"ID": int}).drop_duplicates("ID")


def comparable(df: pd.DataFrame) -> pd.DataFrame:
    """Values as text, so that 1 and 1.0 (or NaN and None) compare equal."""
    num = df.apply(pd.to_numeric, errors="coerce")
    text = df.astype(str).apply(lambda s: s.str.strip())
    out = text.where(num.isna(), num.astype(float).astype(str))
    return out.where(df.notna(), "")


def changed_columns(old: pd.DataFrame, new: pd.DataFrame) -> pd.Series:
    """Number of changed values per column, on the patients and columns both versions share."""
    old, new = old.set_index("ID"), new.set_index("ID")
    ids, cols = old.index.intersection(new.index), old.columns.intersection(new.columns)
    diff = comparable(old.loc[ids, cols]) != comparable(new.loc[ids, cols])
    return diff.sum()[lambda s: s > 0].sort_values(ascending=False)


def natural_key(path: Path) -> list:
    """Sort key that compares the numbers in a file name as numbers: '2_x' before '10_x'."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def read_text(path: Path) -> str:
    """Read a text file as UTF-8, falling back to Latin-1 for older exports."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def parse_number(value: str | None) -> float | None:
    """Extract the number from header values such as '500Hz' -> 500.0"""
    match = re.search(r"\d+(?:\.\d+)?", value or "")
    return float(match.group()) if match else None


def normalize_site(name) -> str | None:
    """Common valve code ('Aórtica' -> 'AV'), None if empty."""
    clean = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().strip().lower()
    return None if clean in ("", "nan") else SITE_MAP.get(clean, str(name))

# ---------------------------------------------------------------- Report de-identification


def has_name(report, name) -> bool:
    """True if any part of the name with 4 or more letters appears in the report."""
    parts = [p for p in str(name).split() if len(p) >= 4]
    return any(re.search(rf"\b{re.escape(p)}\b", str(report), re.IGNORECASE) for p in parts)


def name_field(text):
    """Words in capitals right after 'Nome:', up to the next label (None if there is no 'Nome:')."""
    m = re.search(r"Nome:[ \t]*([^\n]*)", str(text))
    if not m:
        return None
    words = m.group(1).split()
    for i, w in enumerate(words):
        if "NSC:" in w:                                              # label glued to the name
            return " ".join(words[:i] + [w.split("NSC:")[0]]).strip()
        if w.endswith(":") or not w.isupper() or "º" in w:           # next label of the header
            return " ".join(words[:i])
    return " ".join(words)


def deidentify_report(text, name=None) -> str:
    """Replace the 'Nome:' field (everywhere), identifier numbers and any part of the known name."""
    text = str(text)
    field = name_field(text)
    if field:
        text = text.replace(field, "[NAME]")                       # every occurrence, not only in the header
    text = re.sub(r"(NSC:|Nº)\s*\d+", r"\1 [ID]", text)
    text = re.sub(r"\b\d{6,}\b", "[ID]", text)                     # process/episode numbers without a label
    for part in str(name).split() if isinstance(name, str) else []:
        if len(part) >= 4:
            text = re.sub(rf"\b{re.escape(part)}\b", "[NAME]", text, flags=re.IGNORECASE)
    return text

# ---------------------------------------------------------------- Readers


@dataclass
class Signal:
    data: np.ndarray
    fs: float
    meta: dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return len(self.data) / self.fs


TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")   # a data row starts with a timestamp


def read_new_app_csv(path: Path) -> Signal:
    """New app CSV: 'key=value' header lines, then one row per packet (timestamp, samples)."""
    header, packet_times, packets = {}, [], []
    for line in read_text(path).splitlines():
        line = line.strip().rstrip(",")
        if TIMESTAMP_RE.match(line):
            stamp, *values = line.split(",")
            packet_times.append(stamp)
            packets.append(np.array([v for v in values if v.strip()], dtype=float))
        elif "=" in line:
            key, value = line.split("=", 1)
            header[key.strip()] = value.strip()

    fs = parse_number(header.get("Sampling_frequency"))
    data = np.concatenate(packets) if packets else np.empty(0)
    return Signal(data, fs, {"header": header, "packet_times": packet_times,
                             "packet_sizes": [len(p) for p in packets]})


def read_rijuven_ecg(path: Path) -> Signal:
    """Rijuven .raw ECG: comma-separated numbers at 500 Hz."""
    values = [v for v in re.split(r"[,\s]+", read_text(path).strip()) if v]
    return Signal(np.array(values, dtype=float), RIJUVEN_ECG_FS)


def read_rijuven_pcg(path: Path) -> Signal:
    """Rijuven .mp3 PCG at its native sampling rate, stereo averaged to mono."""
    data, fs = sf.read(path, always_2d=True)
    return Signal(data.mean(axis=1), float(fs))


def drop_zero_packets(sig: Signal) -> Signal:
    """Remove the packets made only of zeros (lost packets the app filled in). New app only."""
    size = parse_number(sig.meta.get("header", {}).get("Packages_size"))
    if size is None:
        return sig
    packets = sig.data.reshape(-1, int(size))
    keep = ~(packets == 0).all(axis=1)
    return Signal(packets[keep].ravel(), sig.fs, sig.meta | {"zero_packets": int((~keep).sum())})


def load_recording(row, drop_zeros: bool = True) -> tuple[Signal, Signal]:
    """ECG and PCG of one row of the recording index (zero-filled packets removed by default)."""
    if row["app"] == "rijuven":
        return read_rijuven_ecg(row["ecg_path"]), read_rijuven_pcg(row["pcg_path"])
    ecg, pcg = read_new_app_csv(row["ecg_path"]), read_new_app_csv(row["pcg_path"])
    return (drop_zero_packets(ecg), drop_zero_packets(pcg)) if drop_zeros else (ecg, pcg)

# ---------------------------------------------------------------- Recording index

RIJUVEN_RE = re.compile(r"^(\d+)_([A-Za-z]+).*\.(raw|mp3)$")   # patient, site, extension
NEW_APP_RE = re.compile(r"^[^_]+_(.+?)_(ECG|PCG)_(.+)\.csv$")   # valve, signal, timestamp


def index_rijuven() -> pd.DataFrame:
    """One row per Rijuven recording: the .raw (ECG) and .mp3 (PCG) with the same name."""
    rows = {}
    for path in RIJUVEN_DIR.iterdir():
        patient, site, ext = RIJUVEN_RE.match(path.name).groups()
        row = rows.setdefault(path.stem, {"patient": int(patient), "app": "rijuven", "site": normalize_site(site)})
        row["ecg_path" if ext == "raw" else "pcg_path"] = path
    return pd.DataFrame(rows.values())


def index_new_app() -> pd.DataFrame:
    """One row per new app recording: the ECG and PCG CSVs with the same timestamp."""
    rows = {}
    for path in NEW_APP_DIR.glob("*/*.csv"):
        valve, signal, stamp = NEW_APP_RE.match(path.name).groups()
        row = rows.setdefault((path.parent.name, stamp), {"patient": int(path.parent.name), "app": "new_app", "site": None})
        row["ecg_path" if signal == "ECG" else "pcg_path"] = path
        row["site"] = row["site"] or normalize_site(valve)   # the valve may be filled in only one of the two files
    return pd.DataFrame(rows.values())


def build_index() -> pd.DataFrame:
    """All usable recordings, in recording order within each patient and site."""
    rec = pd.concat([index_rijuven(), index_new_app()], ignore_index=True)
    rec = rec[~rec["patient"].isin(NO_SIGNAL_IDS)]
    rec = rec[(rec["app"] == "new_app") | (rec["patient"] <= RIJUVEN_MAX_ID)]
    rec = rec.assign(name=rec["ecg_path"].map(lambda p: p.stem))   # file names sort in recording order
    return rec.sort_values(["patient", "site", "name"], ignore_index=True)