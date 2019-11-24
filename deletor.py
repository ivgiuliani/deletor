#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import time

from pathlib import Path


logging.basicConfig(level=logging.INFO)


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
                logging.info("Deleting %s" % entry.path)
                if not dry_run:
                    os.remove(entry.path)
        elif entry.is_dir():
            dir_path = Path(entry.path)
            is_empty = len(list(dir_path.rglob('*'))) == 0
            if is_empty:
                logging.info("Deleting empty directory %s" % entry.path)
                if not dry_run:
                    dir_path.rmdir()


def run(base_dir: Path, dry_run: bool, delete_after_seconds: int, check_interval_seconds: int = 60) -> None:
    if dry_run:
        logging.info("DRY RUN ENABLED: no files will be deleted")
    logging.info("Checking %s for files every %d seconds" % (base_dir, check_interval_seconds))
    while True:
        delete(base_dir, dry_run, delete_after_seconds)
        if check_interval_seconds <= 0:
            return
        time.sleep(check_interval_seconds)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("delete_after_seconds",
            type=int,
            help="Delete files in <root> after this many seconds from their creation")
    parser.add_argument("root",
            help="Recursively delete files under this directory")
    parser.add_argument("--dry-run", help="do not actually delete anything", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        run(Path(args.root), dry_run=args.dry_run, delete_after_seconds=args.delete_after_seconds)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sys.exit(main())

