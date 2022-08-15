from datetime import datetime
from ipaddress import IPv4Interface, ip_interface
from typing import cast

from stunning_octo_spork import LogEntry, __version__


def test_version() -> None:
    assert __version__ == "0.1.0"


class TestLogEntry:
    def test_from_list(self) -> None:
        timestamp = datetime(2020, 10, 19, 13, 31, 24)
        srv_addr = cast(IPv4Interface, ip_interface("10.20.30.1/16"))
        expect = LogEntry(timestamp, srv_addr, 2)
        actual = LogEntry.from_list(["20201019133124", "10.20.30.1/16", "2"])
        assert expect == actual
