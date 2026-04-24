#!/usr/bin/env python

import re
from collections import defaultdict
from dataclasses import dataclass


def parse_filename(filename: str):
    PATTERN: re.Pattern[str] = re.compile(r"^(.+?)\.(\d+)\.([^.]+)$")

    match = PATTERN.match(filename)
    if not match:
        return None

    return match.groups()


def _run_to_str(run: list[int]) -> str:
    if len(run) == 1:
        return str(run[0])

    stride = run[1] - run[0]
    if stride == 1:
        return f"{run[0]}-{run[-1]}"

    return f"{run[0]}-{run[-1]}x{stride}"


class Frames(list):
    """Frame numbers that make up a sequence."""

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
        run = [self[0]]

        for frame in self[1:]:
            run_stride = run[1] - run[0] if len(run) > 1 else frame - run[0]
            if frame == run[-1] + run_stride:
                run.append(frame)
            else:
                runs.append(_run_to_str(run))
                run = [frame]

        runs.append(_run_to_str(run))
        return ",".join(runs)

    @property
    def stride(self) -> int:
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
        self.sort()
        return self[0]

    @property
    def last(self) -> int:
        self.sort()
        return self[-1]


@dataclass(frozen=True)
class SequenceIdentifier(object):
    name: str
    padding: int
    ext: str


class Sequences(defaultdict):
    """
    Dictionary of sequence identifiers and found frames.

    { SequenceIdentifier: list[int] }

    Example:
        sequences = Sequences()
        sequences.scan(["foo.0001.exr", "foo.0002.exr"])

        >> { SequenceIdentifier("foo", 4, "exr"): [1, 2] }
    """

    def __init__(self) -> None:
        super().__init__(Frames)

    def scan(self, filenames: list[str]) -> None:
        for filename in filenames:
            result = parse_filename(filename)
            if result is None:
                continue

            name, frame_num, ext = result
            key = SequenceIdentifier(name, len(frame_num), ext)
            self[key].append(int(frame_num))

    def format(self) -> list[str]:
        out = []

        for k, v in self.items():
            pad = k.padding if k.padding > 1 else ""
            cur_row = f"{k.name}.{str(v)}#{pad}.{k.ext}"
            out.append(cur_row)

        return out
