from pathlib import Path

from stunning_octo_spork.cli import Args


class TestArgs:
    def test_parse_args(self) -> None:
        args = Args.parse_args(["log.csv"])
        assert args.log == Path("log.csv")
