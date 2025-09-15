#!/usr/bin/env python

import argparse
import json
import subprocess
from pathlib import Path


def find_files(target: Path) -> list[Path]:
    result = subprocess.check_output(["git", "ls-files", "-z"], cwd=target)
    return [target / Path(p) for p in result.decode().split("\0") if p]


def collect_locs(target: Path):
    locs = {}
    for file in find_files(target):
        with open(file, errors="ignore") as f:
            loc = sum(1 for _ in f)

        locdir = locs
        for part in file.relative_to(target).parent.parts:
            locdir = locdir.setdefault(part, {})
        locdir[file.name] = loc
    return locs


def append_result(output: Path, metric: str, value: int) -> None:
    print(f"{metric} -> {value}")
    with open(output, "a") as f:
        f.write(json.dumps({"metric": metric, "value": value}) + "\n")


def count_and_output_locs(output: Path, path: Path, locs) -> int:
    if isinstance(locs, int):
        append_result(output, f"files/{path}//loc", locs)
        return locs

    total = 0
    for name, child in locs.items():
        total += count_and_output_locs(output, path / name, child)
    if path == Path():
        append_result(output, "files//loc", total)
    else:
        append_result(output, f"files/{path}//loc", total)
    return total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        type=Path,
        help="path to the repo to be benchmarked",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="path the output file should be written to",
    )
    args = parser.parse_args()

    locs = collect_locs(args.target)
    count_and_output_locs(args.output, Path(), locs)


if __name__ == "__main__":
    main()
