import pytest

from handrail.dimensions import DimensionError, format_ft_in, parse, parse_inches


@pytest.mark.parametrize(
    "entered, inches",
    [
        # The four forms named in the brief
        ("5' 6-1/8\"", 66.125),
        ("66.125 in", 66.125),
        ("3 ft 6 in", 42.0),
        ("42", 42.0),
        # Common variants
        ("5'-6 1/8\"", 66.125),
        ("5'6\"", 66.0),
        ("5' 6", 66.0),
        ("7'", 84.0),
        ("7'-0\"", 84.0),
        ("7 ft", 84.0),
        ("3 feet 6 inches", 42.0),
        ("84 inches", 84.0),
        ("84\"", 84.0),
        ("1/2", 0.5),
        ("1/2\"", 0.5),
        (".75 in", 0.75),
        ("0.75", 0.75),
        ("2.5'", 30.0),
        ("  42  ", 42.0),
        ("3 FT 6 IN", 42.0),
        # Typographic quotes pasted from Word or email
        ("5′ 6″", 66.0),
        ("5’ 6”", 66.0),
    ],
)
def test_accepted_forms(entered, inches):
    assert parse_inches(entered) == pytest.approx(inches, rel=1e-12)


@pytest.mark.parametrize(
    "entered",
    [
        "",
        "   ",
        "abc",
        "5 6",          # two bare numbers: feet? inches? refuse to guess
        "-42",          # negative
        "5' 14\"",      # inches >= 12 after feet: likely typo
        "5' 12",
        "1/0",          # zero denominator
        "6 m",          # metric not accepted in v1
        "42 mm",
        "5'' 6'",       # inch mark before foot mark
        "ft",
        "1,000",
    ],
)
def test_rejected_forms(entered):
    with pytest.raises(DimensionError):
        parse_inches(entered)


def test_error_message_names_the_input():
    with pytest.raises(DimensionError, match="5 6"):
        parse_inches("5 6")


@pytest.mark.parametrize(
    "inches, text",
    [
        (42, "3'-6\""),
        (84, "7'-0\""),
        (66.125, "5'-6 1/8\""),
        (0.5, "1/2\""),
        (6, "6\""),
        (12, "1'-0\""),
        (66.1, "5'-6.1\""),  # not an exact sixteenth: decimal, not rounded
    ],
)
def test_format_ft_in(inches, text):
    assert format_ft_in(inches) == text


def test_parse_returns_pint_length_and_echo():
    d = parse("72")
    assert d.value.m_as("ft") == pytest.approx(6.0)
    assert d.normalized == "6'-0\""
    assert d.entered == "72"
