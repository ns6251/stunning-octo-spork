from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Interface
from typing import Final

from .logentry import LogEntry


@dataclass(frozen=True)
class Period:
    begin: datetime
    end: datetime | None


class ServerDownDetector:
    __N: Final[int]
    __timedouts: defaultdict[IPv4Interface, list[datetime]]
    __downed: list[tuple[IPv4Interface, Period]]

    def __init__(self, n: int) -> None:
        self.__N = n
        self.__timedouts = defaultdict(list)
        self.__downed = list()

    def add(self, entry: LogEntry) -> None:
        if entry.ping is None:
            self.__timedouts[entry.addr].append(entry.timestamp)
            return

        if entry.addr in self.__timedouts:
            timedout = self.__timedouts.pop(entry.addr)
            if len(timedout) >= self.__N:
                period = Period(min(timedout), entry.timestamp)
                self.__downed.append((entry.addr, period))

    def detect(self) -> list[tuple[IPv4Interface, Period]]:
        it = filter(lambda x: len(x[1]) >= self.__N, self.__timedouts.items())
        cur_down = [(itf, Period(min(t), None)) for itf, t in it]

        return sorted(self.__downed + cur_down, key=lambda x: x[1].begin)
