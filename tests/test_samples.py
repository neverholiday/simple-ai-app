from app.routes.extract import SAMPLES_DIR, list_samples, read_sample


def test_four_samples_exist():
    assert list_samples() == [
        "01-nam-prik-kapi",
        "02-abbreviations",
        "03-unknown-units",
        "04-restaurant-review",
    ]


def test_samples_are_read_as_utf8_thai():
    assert "น้ำพริกกะปิ" in read_sample("01-nam-prik-kapi")
    assert "ทัพพี" in read_sample("03-unknown-units")


def test_samples_have_lf_line_endings():
    """CRLF from a Windows checkout would change the text sent to the model."""
    for path in SAMPLES_DIR.glob("*.txt"):
        assert b"\r\n" not in path.read_bytes(), path.name


def test_unknown_sample_name_reads_nothing():
    assert read_sample("../pyproject") == ""
