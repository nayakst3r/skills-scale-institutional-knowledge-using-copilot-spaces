"""Parse NEM12 interval-data files into flat interval reads.

NEM12 is AEMO's meter data file format. The records used here:
  100  header         100,NEM12,<datetime>,<from participant>,<to participant>
  200  NMI details    200,<NMI>,<config>,<register>,<suffix>,<stream id>,<meter serial>,<UOM>,<interval length>,<next read>
  300  interval data  300,<YYYYMMDD>,<v1>…<vN>,<quality method>,<reason code>,<reason text>,<updated>,<MSATS load>
  900  end of data

N = 1440 / interval length. A malformed file is rejected as a whole (ARCHITECTURE.md section 7).
Usage:  python -m kestrel.ingestion.nem12 <nem12 file> [<nem12 file> …] --out landing/interval_reads.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from kestrel.shared import config

QUALITY_METHODS = {
    "A",
    "E",
    "F",
    "N",
    "S",
    "V",
}  # actual, estimated, final substitute, null, substitute, variable


class Nem12Error(ValueError):
    """The file is not valid NEM12. Carries the file and line so the provider can be told exactly what to fix."""

    def __init__(self, source: str, line: int, problem: str):
        super().__init__(f"{source}:{line}: {problem}")
        self.source, self.line, self.problem = source, line, problem


@dataclass(frozen=True)
class IntervalRead:
    nmi: str
    nmi_suffix: str
    uom: str
    interval_minutes: int
    read_date: str  # ISO date, market time (AEST)
    interval_number: int  # 1-based
    interval_start: str  # ISO datetime, market time (AEST)
    kwh: str  # decimal as text, exactly as supplied
    quality: str  # first letter of the quality method
    source_file: str
    source_line: int


def parse(lines: list[str], source: str) -> list[IntervalRead]:
    rows = list(csv.reader(lines))
    if not rows or rows[0][:2] != ["100", "NEM12"]:
        raise Nem12Error(source, 1, "first record must be a 100 header for NEM12")
    if rows[-1][:1] != ["900"]:
        raise Nem12Error(source, len(rows), "last record must be 900 (end of data)")

    reads: list[IntervalRead] = []
    nmi_details: list[str] | None = None
    for n, rec in enumerate(rows[1:-1], start=2):
        kind = rec[0] if rec else ""
        if kind == "200":
            if len(rec) < 9:
                raise Nem12Error(source, n, "200 record has fewer than 9 fields")
            try:
                minutes = int(rec[8])
            except ValueError:
                raise Nem12Error(source, n, f"interval length {rec[8]!r} is not a number") from None
            if minutes not in (5, 15, 30):
                raise Nem12Error(source, n, f"interval length {minutes} is not 5, 15 or 30 minutes")
            nmi_details = rec
        elif kind == "300":
            if nmi_details is None:
                raise Nem12Error(source, n, "300 record before any 200 record")
            reads.extend(_intervals(rec, nmi_details, source, n))
        elif kind in {"400", "500"}:
            continue  # quality detail and B2B records: not needed for usage
        else:
            raise Nem12Error(source, n, f"unexpected record type {kind!r}")
    return reads


def _intervals(rec: list[str], nmi: list[str], source: str, line: int) -> list[IntervalRead]:
    minutes = int(nmi[8])
    count = 1440 // minutes
    if len(rec) < 2 + count + 1:
        raise Nem12Error(source, line, f"300 record has {len(rec) - 2} values; expected {count} plus quality")
    try:
        day = datetime.strptime(rec[1], "%Y%m%d").date()
    except ValueError:
        raise Nem12Error(source, line, f"interval date {rec[1]!r} is not YYYYMMDD") from None
    quality = rec[2 + count][:1]
    if quality not in QUALITY_METHODS:
        raise Nem12Error(
            source, line, f"quality method {rec[2 + count]!r} is not one of {sorted(QUALITY_METHODS)}"
        )
    out = []
    for i, raw in enumerate(rec[2 : 2 + count], start=1):
        try:
            value = Decimal(raw)
        except InvalidOperation:
            raise Nem12Error(source, line, f"interval {i} value {raw!r} is not a number") from None
        if value < 0:
            raise Nem12Error(source, line, f"interval {i} value {raw} is negative")
        out.append(
            IntervalRead(
                nmi=nmi[1],
                nmi_suffix=nmi[4],
                uom=nmi[7],
                interval_minutes=minutes,
                read_date=day.isoformat(),
                interval_number=i,
                interval_start=_start(day, i, minutes),
                kwh=raw,
                quality=quality,
                source_file=source,
                source_line=line,
            )
        )
    return out


def _start(day: date, interval_number: int, minutes: int) -> str:
    return (
        datetime.combine(day, datetime.min.time()) + timedelta(minutes=minutes * (interval_number - 1))
    ).isoformat()


def write_csv(reads: list[IntervalRead], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(IntervalRead.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(r) for r in reads)


def main(argv: list[str] | None = None) -> int:
    settings = config.load()
    ap = argparse.ArgumentParser(prog="python -m kestrel.ingestion.nem12")
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=settings.landing_dir / "interval_reads.csv")
    a = ap.parse_args(argv)
    reads: list[IntervalRead] = []
    for f in a.files:
        try:
            reads.extend(parse(f.read_text().splitlines(), f.name))
        except Nem12Error as err:
            print(f"rejected {err}", file=sys.stderr)
            return 1
    write_csv(reads, a.out)
    print(f"{len(reads)} interval reads from {len(a.files)} file(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
