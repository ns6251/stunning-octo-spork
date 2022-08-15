import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, cast

from .detect import ServerDownDetector
from .logentry import LogEntry


@dataclass(frozen=True)
class Args:
    log: Path
    n: int

    @staticmethod
    def parse_args(argv: Sequence[str] | None = None) -> "Args":
        """
        コマンドライン引数のパースをする．

        `argv` が `None` の場合は `sys.argv` のパースをする．(default)
        `argv` が `Sequence[str]` の場合は `argv` のパースをする．
        """
        parser = argparse.ArgumentParser(description="監視ログの統計")
        parser.add_argument("path", nargs="?", type=Path, help="読み込む監視ログのパス")
        parser.add_argument("-n", nargs="?", default=1, type=int, help="故障判定に必要な連続タイムアウトの回数", metavar="N")
        args = parser.parse_args(argv)
        log = cast(Path, args.path)
        return Args(log, cast(int, args.n))


def main() -> None:
    args = Args.parse_args()

    sdd = ServerDownDetector()

    with open(args.log, mode="r", encoding="utf8") as f:
        reader = csv.reader(f)
        log_entries = map(LogEntry.from_list, reader)

        for entry in log_entries:
            sdd.add(entry)

    for down in sdd.detect():
        itf, period = down
        begin = period.begin.strftime(r"%Y%m%d%H%M%S")
        end = period.end.strftime(r"%Y%m%d%H%M%S") if period.end else "-"
        print(f"{itf.with_prefixlen},{begin},{end}")
