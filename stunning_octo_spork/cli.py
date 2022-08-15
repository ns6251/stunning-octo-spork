import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, cast

from .logentry import LogEntry


@dataclass(frozen=True)
class Args:
    log: Path

    @staticmethod
    def parse_args(argv: Sequence[str] | None = None) -> "Args":
        """
        コマンドライン引数のパースをする．

        `argv` が `None` の場合は `sys.argv` のパースをする．(default)
        `argv` が `Sequence[str]` の場合は `argv` のパースをする．
        """
        parser = argparse.ArgumentParser(description="監視ログの統計")
        parser.add_argument("path", nargs="?", type=Path, help="読み込む監視ログのパス")
        args = parser.parse_args(argv)
        log = cast(Path, args.path)
        return Args(log)


def main() -> None:
    args = Args.parse_args()

    with open(args.log, mode="r", encoding="utf8") as f:
        reader = csv.reader(f)
        log_entries = map(LogEntry.from_list, reader)

        print(*list(log_entries), sep="\n")
