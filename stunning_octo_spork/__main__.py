import csv

from .logentry import LogEntry

with open("log.csv", mode="r", encoding="utf8") as f:
    reader = csv.reader(f)
    log_entries = map(LogEntry.from_list, reader)

    print(*list(log_entries), sep="\n")
