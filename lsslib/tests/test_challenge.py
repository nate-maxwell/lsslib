import lsslib


def test_frame_list() -> None:
    assert str(lsslib.FrameList([1])) == "1"
    assert str(lsslib.FrameList([1, 2, 3, 4])) == "1-4"
    assert str(lsslib.FrameList([5, 6, 7])) == "5-7"
    assert str(lsslib.FrameList([0, 5, 10, 15])) == "0-15x5"
    assert str(lsslib.FrameList([1, 2, 3, 5, 6, 7])) == "1-3,5-7"


def test_parse_filename() -> None:
    assert lsslib.parse_frame_name("foo.0001.exr") == ("foo", "0001", "exr")
    assert lsslib.parse_frame_name("foo.001.jpg") == ("foo", "001", "jpg")
    assert lsslib.parse_frame_name("foo.1.png") == ("foo", "1", "png")
    assert lsslib.parse_frame_name("foo.bar.0100.exr") == ("foo.bar", "0100", "exr")


def test_sequences() -> None:
    files = [
        "foo.0000.exr",
        "foo.0001.exr",
        "foo.0002.exr",
        "foo.0003.exr",
        "foo.0004.exr",
    ]
    seq_table, _ = lsslib.scan_filenames(files)

    expected_identifier = lsslib.SequenceIdentifier("foo", 4, "exr")
    assert expected_identifier in seq_table
    assert seq_table[expected_identifier] == [0, 1, 2, 3, 4]


def test_sequences_discontiguous() -> None:
    files = [
        "foo.0001.exr",
        "foo.0002.exr",
        "foo.0003.exr",
        "foo.0005.exr",
        "foo.0006.exr",
        "foo.0007.exr",
    ]
    seq_table, _ = lsslib.scan_filenames(files)

    expected_identifier = lsslib.SequenceIdentifier("foo", 4, "exr")
    assert expected_identifier in seq_table
    assert seq_table[expected_identifier] == [1, 2, 3, 5, 6, 7]


def test_contiguous_same_pad() -> None:
    files = [
        "foo.0000.exr",
        "foo.0001.exr",
        "foo.0002.exr",
        "foo.0003.exr",
        "foo.0004.exr",
    ]
    seq_table, _ = lsslib.scan_filenames(files)
    results = seq_table.format()

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
    seq_table, _ = lsslib.scan_filenames(files)
    result = seq_table.format()

    assert result == ["foo.1-3,5-7#4.exr"]


def test_stride_five() -> None:
    files = ["foo.0000.exr", "foo.0005.exr", "foo.0010.exr", "foo.0015.exr"]
    seq_table, _ = lsslib.scan_filenames(files)
    result = seq_table.format()

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
    seq_table, _ = lsslib.scan_filenames(files)
    result = seq_table.format()

    assert result == ["foo.1-3#4.exr", "foo.1-3#3.exr"]


def test_non_padded() -> None:
    files = ["foo.0.exr", "foo.1.exr", "foo.2.exr", "foo.3.exr"]
    seq_table, _ = lsslib.scan_filenames(files)
    result = seq_table.format()

    assert result == ["foo.0-3#.exr"]
