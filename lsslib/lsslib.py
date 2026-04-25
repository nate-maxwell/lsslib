#!/usr/bin/env python3

"""
lsslib, a small library for listing image sequences in a directory.

usage: lss [-h] [-a] [paths ...]
    -h help
    -a list all items
"""

import argparse
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


def parse_frame_name(filename: str) -> tuple | None:
    """
    Returns the name, frame_num, ext of an image frame formatted as "foo.0001.exr"
    if it can be determined else None.
    """
    PATTERN: re.Pattern[str] = re.compile(r"^(.+?)\.(\d+)\.([^.]+)$")

    match = PATTERN.match(filename)
    if not match:
        return None

    return match.groups()


def _run_to_str(run: list[int]) -> str:
    """Formats a single run of frame numbers as a compact string."""
    if len(run) == 1:
        return str(run[0])

    stride = run[1] - run[0]
    if stride == 1:
        return f"{run[0]}-{run[-1]}"

    return f"{run[0]}-{run[-1]}x{stride}"


class FrameList(list):
    """
    A sorted list of integer frame numbers belonging to a single image sequence.

    Subclasses list and adds sequence-aware properties and string formatting.
    String representation encodes the frame range compactly:

        [1, 2, 3, 4]        -> "1-4"
        [0, 5, 10, 15]      -> "0-15x5"
        [1, 2, 3, 5, 6, 7]  -> "1-3,5-7"
        [1]                 -> "1"
        []                  -> ""

    Properties:
        stride (int): The incrementation stride of the images.
        first (int): The first frame number.
        last (int): The last frame number.
    """

    def __str__(self) -> str:
        self.sort()

        if len(self) == 0:
            return ""

        if len(self) == 1:
            return str(self[0])

        stride = self.stride

        if stride != 0:
            if stride == 1:
                return f"{self.first}-{self.last}"
            return f"{self.first}-{self.last}x{stride}"

        # Gapped — break into contiguous runs and join with commas
        runs: list[str] = []
        run: list[int] = [self[0]]

        # Walk frames starting from the second, building up runs of consistent stride.
        # On the first step into a new run we don't know the stride yet, so we derive
        # it from the gap between the current frame and the single element in run.
        # Once run has two or more elements the stride is fixed as run[1] - run[0].
        for frame in self[1:]:
            run_stride = run[1] - run[0] if len(run) > 1 else frame - run[0]
            if frame == run[-1] + run_stride:
                # Frame continues the current run at the expected stride.
                run.append(frame)
            else:
                # Stride broke — flush the completed run and start a new one.
                runs.append(_run_to_str(run))
                run = [frame]

        runs.append(_run_to_str(run))
        return ",".join(runs)

    @property
    def stride(self) -> int:
        """
        Stride is the uniform step size between frames, or 0 if there is no
        consistent stride (i.e. the sequence has gaps or mixed increments).
        """
        self.sort()

        if len(self) < 2:
            return 1

        stride = self[1] - self[0]
        for i in range(2, len(self)):
            if self[i] != self[i - 1] + stride:
                return 0

        return stride

    @property
    def first(self) -> int:
        """The lowest frame number."""
        self.sort()
        return self[0]

    @property
    def last(self) -> int:
        """The highest frame number."""
        self.sort()
        return self[-1]

    @property
    def contiguous(self) -> bool:
        """Whether the frame list has a uniform stride (no gaps)."""
        return self.stride != 0


@dataclass(frozen=True)
class SequenceIdentifier(object):
    name: str
    padding: int
    ext: str


class SequenceDict(defaultdict[SequenceIdentifier, FrameList]):
    """
    Dictionary of sequence identifiers and found frames.

    { SequenceIdentifier: list[int] }

    Example:
        sequences = Sequences()
        sequences.scan(["foo.0001.exr", "foo.0002.exr"])

        >> { SequenceIdentifier("foo", 4, "exr"): [1, 2] }
    """

    def __init__(self) -> None:
        super().__init__(FrameList)

    def to_strings(self) -> list[str]:
        out = []

        for k, v in self.items():
            pad = k.padding if k.padding > 1 else ""
            cur_row = f"{k.name}.{str(v)}#{pad}.{k.ext}"
            out.append(cur_row)

        return out


def scan_filenames(filenames: list[str]) -> tuple[SequenceDict, list[str]]:
    """Returns a populated Sequences dict and a list of non-frame files."""
    non_img_files = []
    seq_dict = SequenceDict()

    for filename in filenames:
        parsed = parse_frame_name(filename)
        if parsed is None:
            non_img_files.append(filename)
            continue

        name, frame_num, ext = parsed
        key = SequenceIdentifier(name, len(frame_num), ext)
        seq_dict[key].append(int(frame_num))

    non_img_files.sort()

    return seq_dict, non_img_files


def scan_dir(path: str | os.PathLike) -> tuple[SequenceDict, list[str]]:
    """
    Returns a populated Sequences dict and a list of non-frame files from a
    directory.

    Raises ValueError if path is not dir.
    """
    p = Path(path)
    if not p.is_dir():
        raise ValueError(f"{p.as_posix()} is not a directory!")

    filenames = [f.name for f in p.iterdir()]
    return scan_filenames(filenames)


def lss(path: str | os.PathLike, all_files: bool = False) -> None:
    """
    Print image sequences found in a directory, one per line.

    Args:
        path (str | os.PathLike): Directory to scan.
        all_files (bool): If True, also print non-sequence files after sequences.
    """
    seq_dict, others = scan_dir(path)
    seqs = seq_dict.to_strings()

    for i in seqs:
        print(i)

    if not others or not all_files:
        return
    for i in others:
        print(i)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="lss", description="List image sequences in a directory."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Directories to list (default: current directory).",
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Also list non-sequence files."
    )
    args = parser.parse_args()

    for path in args.paths:
        if len(args.paths) > 1:
            print(f"{path}:")

        lss(path, args.all)


if __name__ == "__main__":
    main()
