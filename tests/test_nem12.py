from decimal import Decimal

import pytest

from kestrel.ingestion.nem12 import Nem12Error, parse

HEADER = "100,NEM12,202610170700,MDPX,KESTREL"
NMI = "200,4103000001,E1,1,E1,N1,MTR0001,KWH,30,20261115"
END = "900"


def day(values, date="20261016", quality="A"):
    return ",".join(["300", date, *values, quality, "", "", "20261017063000", "20261017070000"])


def test_parses_48_half_hour_intervals_in_market_time():
    values = ["0.250"] * 47 + ["1.125"]
    reads = parse([HEADER, NMI, day(values), END], "sample.csv")
    assert len(reads) == 48
    assert reads[0].interval_start == "2026-10-16T00:00:00"
    assert reads[-1].interval_start == "2026-10-16T23:30:00"
    assert reads[-1].kwh == "1.125"
    assert sum(Decimal(r.kwh) for r in reads) == Decimal("12.875")
    assert {r.nmi for r in reads} == {"4103000001"}
    assert reads[0].source_line == 3


def test_rejects_a_file_without_the_end_record():
    with pytest.raises(Nem12Error, match="last record must be 900"):
        parse([HEADER, NMI, day(["0.1"] * 48)], "cut.csv")


def test_rejects_a_short_interval_record_with_its_line():
    with pytest.raises(Nem12Error) as err:
        parse([HEADER, NMI, day(["0.1"] * 47), END], "short.csv")
    assert err.value.line == 3


def test_rejects_negative_usage():
    with pytest.raises(Nem12Error, match="negative"):
        parse([HEADER, NMI, day(["0.1"] * 47 + ["-0.5"]), END], "neg.csv")


def test_rejects_unknown_quality_method():
    with pytest.raises(Nem12Error, match="quality method"):
        parse([HEADER, NMI, day(["0.1"] * 48, quality="Q"), END], "q.csv")
