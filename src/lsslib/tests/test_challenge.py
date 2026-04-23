from src.lsslib.scanner import group_files


def test_contiguous_same_pad() -> None:
    files = [
        "foo.0000.exr",
        "foo.0001.exr",
        "foo.0002.exr",
        "foo.0003.exr",
        "foo.0004.exr",
    ]
    results = group_files(files)

    assert results == ["foo.0-4#4.exr"]


def test_discontiguous_same_pad() -> None:
    files = [
        "foo.0001.exr",
        "foo.0002.exr",
        "foo.0003.exr",
        "foo.0005.exr",
        "foo.0006.exr",
        "foo.0007.exr",
    ]
    result = group_files(files)

    assert result == ["foo.1-3,5-7#4.exr"]


def test_stride_five() -> None:
    files = [
        "foo.0000.exr",
        "foo.0005.exr",
        "foo.0010.exr",
        "foo.0015.exr",
        "foo.0020.exr",
        "foo.0025.exr",
    ]
    result = group_files(files)

    assert result == ["foo.0-15x5#4.exr"]


def test_same_seq_dif_padding() -> None:
    files = [
        "foo.0001.exr",
        "foo.0002.exr",
        "foo.0003.exr",
        "foo.001.exr",
        "foo.002.exr",
        "foo.003.exr",
    ]
    result = group_files(files)

    assert result == ["foo.1-3#4.exr", "foo.1-3#3.exr"]


def test_non_padded() -> None:
    files = ["foo.0.exr", "foo.1.exr", "foo.2.exr", "foo.3.exr"]
    result = group_files(files)

    assert result == ["foo.0-3#.exr"]
