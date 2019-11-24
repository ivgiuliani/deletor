#!/usr/bin/env python3

import sys
import os
import glob
import time
from pathlib import Path

def scan_path(path: Path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_path(entry.path)
        yield entry


def delete(base_dir: Path, dry_run: bool, delete_after_seconds: int) -> None:
    for entry in scan_path(base_dir):
        if entry.is_file():
            entry_life_seconds = int(time.time() - os.path.getmtime(entry.path))

            if entry_life_seconds >= delete_after_seconds:
                if not dry_run:
                    os.remove(entry.path)
        elif entry.is_dir():
            dir_path = Path(entry.path)
            is_empty = len(list(dir_path.rglob('*'))) == 0
            if is_empty:
                if not dry_run:
                    dir_path.rmdir()


def main(args):
    if len(args) == 1:
        print("Usage: %s [--dry-run] <delete seconds> <base folder>" % args[0])
        return False
    if args[1] == "--dry-run":
        dry_run = True
        delete_seconds = int(args[2])
        base_folder = Path(args[3])
    else:
        dry_run = False
        delete_seconds = int(args[1])
        base_folder = Path(args[2])

    delete(base_folder, dry_run=dry_run, delete_after_seconds=delete_seconds)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
