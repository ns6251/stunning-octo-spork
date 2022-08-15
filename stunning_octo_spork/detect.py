from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Interface, IPv4Network
from typing import Final

from .logentry import LogEntry


@dataclass
class Period:
    begin: datetime
    end: datetime | None


class DownDetector:
    __N: Final[int]
    __timedouts: defaultdict[IPv4Network, defaultdict[IPv4Interface, list[datetime]]]
    __downed: list[tuple[IPv4Interface, Period]]

    def __make_defaultdict_helper(self) -> defaultdict[IPv4Interface, list[datetime]]:
        return defaultdict(list)

    def __init__(self, n: int) -> None:
        self.__N = n
        self.__timedouts = defaultdict(self.__make_defaultdict_helper)
        self.__downed = list()

    def add(self, entry: LogEntry) -> None:
        if entry.ping is None:
            self.__timedouts[entry.addr.network][entry.addr].append(entry.timestamp)
            return

        if all(map(lambda x: len(x) >= self.__N, self.__timedouts[entry.addr.network].values())):
            pass

        if entry.addr in self.__timedouts[entry.addr.network]:
            timedout = self.__timedouts[entry.addr.network][entry.addr]

            if len(timedout) >= self.__N:
                period = Period(min(timedout), entry.timestamp)
                self.__downed.append((entry.addr, period))

            timedout.clear()

    def detect(self) -> list[tuple[IPv4Interface, Period]]:
        still_down: list[tuple[IPv4Interface, Period]] = []
        for a in self.__timedouts.values():
            it = filter(lambda x: len(x[1]) >= self.__N, a.items())
            still_down += [(itf, Period(min(t), None)) for itf, t in it]

        return sorted(self.__downed + still_down, key=lambda x: x[1].begin)


class OverloadDetector:
    __WINDOW_SIZE: Final[int]
    __THRESHOLD: Final[int]
    __history: defaultdict[IPv4Interface, deque[LogEntry]]
    __cur_overload: dict[IPv4Interface, Period]
    __overloaded: list[tuple[IPv4Interface, Period]]

    def __make_deque(self) -> deque[LogEntry]:
        return deque(maxlen=self.__WINDOW_SIZE)

    def __init__(self, window_size: int, threshold: int) -> None:
        self.__WINDOW_SIZE = window_size
        self.__THRESHOLD = threshold
        self.__history = defaultdict(self.__make_deque)
        self.__cur_overload = dict()
        self.__overloaded = list()

    def add(self, entry: LogEntry) -> None:
        recent = self.__history[entry.addr]
        recent.append(entry)

        # サーバーエラーを除外したping
        pings = tuple(filter(None, map(lambda r: r.ping, recent)))

        if len(pings) == self.__WINDOW_SIZE and sum(pings) / len(pings) > self.__THRESHOLD:
            if entry.addr not in self.__cur_overload:
                self.__cur_overload[entry.addr] = Period(entry.timestamp, entry.timestamp)
            else:
                self.__cur_overload[entry.addr].end = entry.timestamp
        else:
            if entry.addr in self.__cur_overload:
                cur_period = self.__cur_overload.pop(entry.addr)
                self.__overloaded.append((entry.addr, cur_period))

    def detect(self) -> list[tuple[IPv4Interface, Period]]:
        still = list(self.__cur_overload.items())
        return sorted(self.__overloaded + still, key=lambda x: x[1].begin)
