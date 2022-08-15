from datetime import datetime
from ipaddress import IPv4Interface, IPv4Network, ip_interface, ip_network
from typing import cast

from stunning_octo_spork.detect import DownDetector, OverloadDetector, Period, Report
from stunning_octo_spork.logentry import LogEntry


class TestDownDetector:
    def test_healty(self) -> None:
        dd = DownDetector(1)
        dd.add(LogEntry.from_list("20201019133123,10.20.30.2/16,3".split(",")))
        dd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,2".split(",")))
        dd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,522".split(",")))
        assert dd.detect() == []

    def test_downed(self) -> None:
        dd = DownDetector(1)
        dd.add(LogEntry.from_list("20201019133123,10.20.30.2/16,3".split(",")))
        dd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133223,10.20.30.2/16,3".split(",")))
        dd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,522".split(",")))

        begin, end = datetime(2020, 10, 19, 13, 31, 24), datetime(2020, 10, 19, 13, 32, 24)
        expect = [Report(cast(IPv4Interface, ip_interface("10.20.30.1/16")), Period(begin, end))]
        assert dd.detect() == expect

    def test_still_downed(self) -> None:
        dd = DownDetector(1)
        dd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))

        begin = datetime(2020, 10, 19, 13, 32, 24)
        expect = [Report(cast(IPv4Interface, ip_interface("10.20.30.1/16")), Period(begin, None))]
        assert dd.detect() == expect

    def test_downed_n(self) -> None:
        dd = DownDetector(3)
        dd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133224,10.20.30.2/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133324,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133424,10.20.30.1/16,3".split(",")))
        begin, end = datetime(2020, 10, 19, 13, 31, 24), datetime(2020, 10, 19, 13, 34, 24)
        expect = [Report(cast(IPv4Interface, ip_interface("10.20.30.1/16")), Period(begin, end))]
        assert dd.detect() == expect

    def test_not_downed_n(self) -> None:
        dd = DownDetector(3)
        dd.add(LogEntry.from_list("20201019133124,10.20.30.1/16,5".split(",")))
        dd.add(LogEntry.from_list("20201019133224,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133224,10.20.30.2/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133324,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133424,10.20.30.1/16,3".split(",")))
        assert dd.detect() == []

    def test_downed_switch(self) -> None:
        dd = DownDetector(3)
        dd.add(LogEntry.from_list("20201019133121,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133122,10.20.30.2/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133221,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133222,10.20.30.2/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133321,10.20.30.1/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133322,10.20.30.2/16,-".split(",")))
        dd.add(LogEntry.from_list("20201019133421,10.20.30.1/16,5".split(",")))
        dd.add(LogEntry.from_list("20201019133422,10.20.30.2/16,3".split(",")))
        begin = datetime(2020, 10, 19, 13, 31, 21)
        end = datetime(2020, 10, 19, 13, 34, 21)
        assert dd.detect() == [Report(cast(IPv4Network, ip_network("10.20.0.0/16")), Period(begin, end))]


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
        expect = [Report(cast(IPv4Interface, ip_interface("10.20.30.1/16")), Period(begin, end))]
        assert old.detect() == expect
