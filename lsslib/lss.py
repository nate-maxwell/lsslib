import argparse

from . import lsslib


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

        lsslib.lss(path, args.all)


if __name__ == "__main__":
    main()
