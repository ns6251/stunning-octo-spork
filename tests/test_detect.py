from datetime import datetime
from ipaddress import ip_interface

from stunning_octo_spork.detect import Period, ServerDownDetector
from stunning_octo_spork.logentry import LogEntry


class TestServerDownDetector:
    def test_healty(self) -> None:
        sdd = ServerDownDetector()
        sdd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,2".split(",")))
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,522".split(",")))
        assert sdd.detect() == []

    def test_downed(self) -> None:
        sdd = ServerDownDetector()
        sdd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,-".split(",")))
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,522".split(",")))

        begin, end = datetime(2020, 10, 19, 13, 31, 24), datetime(2020, 10, 19, 13, 32, 24)
        expect = [(ip_interface("10.20.30.1/16"), Period(begin, end))]
        assert sdd.detect() == expect

    def test_still_downed(self) -> None:
        sdd = ServerDownDetector()
        sdd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))

        begin = datetime(2020, 10, 19, 13, 32, 24)
        expect = [(ip_interface("10.20.30.1/16"), Period(begin, None))]
        assert sdd.detect() == expect
