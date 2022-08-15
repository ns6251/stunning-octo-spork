from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Interface, ip_interface


@dataclass
class LogEntry:
    timestamp: datetime
    srv_addr: IPv4Interface
    ping: int | None

    @classmethod
    def from_list(cls, entry: list[str]) -> "LogEntry":
        timestamp_, srv_addr_, ping_ = entry

        timestamp = datetime.strptime(timestamp_, r"%Y%m%d%H%M%S")
        srv_addr = ip_interface(srv_addr_)

        if type(srv_addr) is not IPv4Interface:
            raise ValueError("server address is not IPv4Interface")

        if ping_ == "-":
            ping: int | None = None
        else:
            ping = int(ping_)

        return LogEntry(timestamp, srv_addr, ping)
