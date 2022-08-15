from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Interface

from .logentry import LogEntry


@dataclass(frozen=True)
class Period:
    begin: datetime
    end: datetime | None


class ServerDownDetector:
    __timedouts: defaultdict[IPv4Interface, list[datetime]]
    __downed: list[tuple[IPv4Interface, Period]]

    def __init__(self) -> None:
        self.__timedouts = defaultdict(list)
        self.__downed = list()

    def add(self, entry: LogEntry) -> None:
        if entry.ping is None:
            self.__timedouts[entry.addr].append(entry.timestamp)
            return

        if entry.addr in self.__timedouts:
            timedout = self.__timedouts.pop(entry.addr)
            period = Period(min(timedout), entry.timestamp)
            self.__downed.append((entry.addr, period))

    def detect(self) -> list[tuple[IPv4Interface, Period]]:
        cur_down = [(itf, Period(min(t), None)) for itf, t in self.__timedouts.items()]

        return sorted(self.__downed + cur_down, key=lambda x: x[1].begin)
