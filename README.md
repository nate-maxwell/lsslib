# lsslib

A Python library and CLI tool for listing image sequences in a directory.

---

Project contains a separate file for the lss cli tool and the lsslib used to
make it.

If the package were to be deployed in rez or another package manager, the `lsslib/`
folder would be placed in a `src/` dir, but for a clean submission I left it as
the bare folder.

Testing was done using pytest, and is outlined in the toml.

The toml also contains `lss:main` in  the `[project.scripts]` section so
it could be run as a terminal command after running `pip install -e <path/to/lsslib>`.

---

### lss CLI Command

Arg parser that invokes library functionality

```
usage: lss [-h] [-a] [paths ...]
    -h help
    -a list all items
```

---

### Library

The library consists of 3 main components and various smaller components:
* `FrameList` - A list of frame numbers that stringifies into a compact representation.
* `SequenceDict` - A dictionary of sequence identifiers to FrameLists with
attributes of the sequence.
* `scan_filenames()` - The primary function that `scan_dir()` and `lss()` are
built on. Separated for easier testing and more flexible library usage.
