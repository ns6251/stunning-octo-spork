from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Interface, IPv4Network
from typing import Final

from .logentry import LogEntry


@dataclass
class Period:
    """期間"""
    begin: datetime
    end: datetime | None


@dataclass
class Report:
    """ネットワークインターフェースとそれに対するイベント（故障・過負荷）の期間"""
    addr: IPv4Interface | IPv4Network
    period: Period


class DownDetector:
    """
    サーバの故障とスイッチの故障を検出する．
    """
    __N: Final[int]
    __timedouts: defaultdict[IPv4Network, dict[IPv4Interface, list[datetime]]]
    __downed: list[Report]

    def __init__(self, n: int) -> None:
        self.__N = n
        self.__timedouts = defaultdict(dict)
        self.__downed = list()

    def __is_switch_downed(self, network: IPv4Network) -> bool:
        return all(map(lambda x: len(x) >= self.__N, self.__timedouts[network].values()))

    def add(self, entry: LogEntry) -> None:
        self.__timedouts[entry.addr.network].setdefault(entry.addr, list())

        if entry.ping is None:
            self.__timedouts[entry.addr.network][entry.addr].append(entry.timestamp)
            return

        if self.__is_switch_downed(entry.addr.network):
            min_timedouts = []
            for timedout in self.__timedouts[entry.addr.network].values():
                min_timedouts.append(min(timedout))
                timedout.clear()
            begin = min(min_timedouts + [entry.timestamp])
            period = Period(begin, entry.timestamp)
            self.__downed.append(Report(entry.addr.network, period))
            return

        timedout = self.__timedouts[entry.addr.network][entry.addr]
        if len(timedout) >= self.__N:
            period = Period(min(timedout), entry.timestamp)
            self.__downed.append(Report(entry.addr, period))
            timedout.clear()

    def detect(self) -> list[Report]:
        still_down = []
        for a in self.__timedouts.values():
            it = filter(lambda x: len(x[1]) >= self.__N, a.items())
            still_down += [Report(itf, Period(min(t), None)) for itf, t in it]

        return sorted(
            self.__downed + still_down,
            key=lambda x: x.period.begin,
        )


class OverloadDetector:
    """
    サーバの過負荷状態を検出する．
    """
    __WINDOW_SIZE: Final[int]
    __THRESHOLD: Final[int]
    __history: defaultdict[IPv4Interface, deque[LogEntry]]
    __cur_overload: dict[IPv4Interface, Period]
    __overloaded: list[Report]

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
                self.__overloaded.append(Report(entry.addr, cur_period))

    def detect(self) -> list[Report]:
        still = list(map(lambda x: Report(*x), self.__cur_overload.items()))
        return sorted(self.__overloaded + still, key=lambda x: x.period.begin)
