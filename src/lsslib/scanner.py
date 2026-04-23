import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union


@dataclass
class SeqShape(object):
    name: str
    start: int
    end: int
    padding: int
    suffix: str

    def __str__(self) -> str:
        s = f"{self.name}.{self.start}-{self.end}#{self.padding}{self.suffix}"
        return s


def group_files(files: list[Union[str, os.PathLike[str]]]) -> list[str]:
    seq_shapes: dict[str, SeqShape] = {}

    for file in files:
        file_path = Path(file)
        parts = file_path.name.split(".")
        seq = parts[0]
        frame = parts[1]
        padding = len(frame)

        shape_key = f"{seq}:{padding}"
        if shape_key in seq_shapes:
            shape = seq_shapes[shape_key]
            shape.end = int(frame)
        else:
            shape = SeqShape(
                name=seq,
                start=int(frame),
                end=int(frame),
                padding=padding,
                suffix=file_path.suffix,
            )

            seq_shapes[shape_key] = shape

    return [str(i) for i in seq_shapes.values()]


def group_files_from_dir(directory: Union[str, os.PathLike[str]]) -> list[str]:
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError("Can only group files on a directory, nothing else...")

    try:
        items = sorted(directory.iterdir(), key=lambda p: p.name.lower())
    except PermissionError:
        raise PermissionError(
            f"lss cannot open directory '{directory.as_posix()}': Permission denied"
        )

    items = [i for i in items if not i.is_file()]
    return group_files(items)
