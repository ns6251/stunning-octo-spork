from datetime import datetime
from ipaddress import ip_interface

from stunning_octo_spork.detect import OverloadDetector, Period, DownDetector
from stunning_octo_spork.logentry import LogEntry


class TestServerDownDetector:
    def test_healty(self) -> None:
        sdd = DownDetector(1)
        sdd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,2".split(",")))
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,522".split(",")))
        assert sdd.detect() == []

    def test_downed(self) -> None:
        sdd = DownDetector(1)
        sdd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,522".split(",")))

        begin, end = datetime(2020, 10, 19, 13, 31, 24), datetime(2020, 10, 19, 13, 32, 24)
        expect = [(ip_interface("10.20.30.1/16"), Period(begin, end))]
        assert sdd.detect() == expect

    def test_still_downed(self) -> None:
        sdd = DownDetector(1)
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))

        begin = datetime(2020, 10, 19, 13, 32, 24)
        expect = [(ip_interface("10.20.30.1/16"), Period(begin, None))]
        assert sdd.detect() == expect

    def test_downed_n(self) -> None:
        sdd = DownDetector(3)
        sdd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133324,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133424,10.20.30.1/16,3".split(",")))
        begin, end = datetime(2020, 10, 19, 13, 31, 24), datetime(2020, 10, 19, 13, 34, 24)
        expect = [(ip_interface("10.20.30.1/16"), Period(begin, end))]
        assert sdd.detect() == expect

    def test_not_downed_n(self) -> None:
        sdd = DownDetector(3)
        sdd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,5".split(",")))
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133324,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133424,10.20.30.1/16,3".split(",")))
        assert sdd.detect() == []


class TestOverloadDetector:
    def test_healty(self) -> None:
        old = OverloadDetector(3, 500)
        old.add(LogEntry.from_list("20201019133124,10.20.30.1/16,2".split(",")))
        old.add(LogEntry.from_list("20201019133224,10.20.30.1/16,0".split(",")))
        old.add(LogEntry.from_list("20201019133324,10.20.30.1/16,500".split(",")))
        old.add(LogEntry.from_list("20201019133424,10.20.30.1/16,1".split(",")))
        assert old.detect() == []

    def test_overload(self) -> None:
        old = OverloadDetector(3, 500)
        old.add(LogEntry.from_list("20201019133124,10.20.30.1/16,600".split(",")))
        old.add(LogEntry.from_list("20201019133224,10.20.30.1/16,500".split(",")))
        old.add(LogEntry.from_list("20201019133324,10.20.30.1/16,500".split(",")))
        old.add(LogEntry.from_list("20201019133424,10.20.30.1/16,1".split(",")))
        begin, end = datetime(2020, 10, 19, 13, 33, 24), datetime(2020, 10, 19, 13, 33, 24)
        expect = [(ip_interface("10.20.30.1/16"), Period(begin, end))]
        assert old.detect() == expect
