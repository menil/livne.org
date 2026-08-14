"""Tests for JSON Resume validation against the official schema."""

from src.validate_resume import validate_resume

VALID_YAML = """\
basics:
  name: "Jane Doe"
  email: "jane.doe@example.com"
  phone: "555-0000"
  summary: "Summary."
  location:
    city: "Seattle"
    region: "WA"
  profiles:
    - network: LinkedIn
      url: "https://linkedin.com/in/jane"
work:
  - name: "Acme"
    position: "Engineer"
    startDate: "2020"
    endDate: "2026"
    highlights:
      - "Bullet"
skills:
  - name: "Languages"
    keywords:
      - "Python"
education:
  - studyType: "B.Sc."
    area: "Computer Science"
    institution: "University"
"""


def _write(tmp_path, content):
    path = tmp_path / "cv.yaml"
    path.write_text(content)
    return str(path)


def test_valid_resume_passes(tmp_path):
    assert validate_resume(_write(tmp_path, VALID_YAML)) == []


def test_placeholders_render_before_validation(tmp_path):
    path = _write(
        tmp_path,
        "basics:\n"
        "  name: '{{ name }}'\n"
        "  email: '{{ email }}'\n"
        "  phone: '{{ phone }}'\n"
        "  profiles:\n"
        "    - network: LinkedIn\n"
        "      url: '{{ linkedin }}'\n"
        "work: []\n",
    )
    assert validate_resume(path) == []


def test_int_dates_rejected(tmp_path):
    path = _write(
        tmp_path,
        "basics:\n  name: X\nwork:\n  - name: Acme\n    position: Dev\n    startDate: 2020\n",
    )
    assert "is not of type 'string'" in validate_resume(path)[0]


def test_year_only_string_date_accepted(tmp_path):
    path = _write(
        tmp_path,
        "basics:\n  name: X\nwork:\n  - name: Acme\n    position: Dev\n    startDate: '2020'\n",
    )
    assert validate_resume(path) == []


def test_year_month_and_full_dates_accepted(tmp_path):
    for date in ("2020-06", "2020-06-29"):
        path = _write(
            tmp_path,
            "basics:\n  name: X\nwork:\n"
            f"  - name: Acme\n    position: Dev\n    startDate: '{date}'\n",
        )
        assert validate_resume(path) == []


def test_bad_email_rejected(tmp_path):
    path = _write(tmp_path, "basics:\n  name: X\n  email: 'not-an-email'\nwork: []\n")
    assert "is not a 'email'" in validate_resume(path)[0]


def test_non_string_highlight_rejected(tmp_path):
    path = _write(
        tmp_path,
        "basics:\n  name: X\nwork:\n"
        '  - name: Acme\n    position: Dev\n    highlights: ["ok", 42]\n',
    )
    assert "is not of type 'string'" in validate_resume(path)[0]


def test_unknown_top_level_key_allowed(tmp_path):
    path = _write(tmp_path, "basics:\n  name: X\nwork: []\nfoo: bar\n")
    assert validate_resume(path) == []


def test_missing_required_fields_allowed(tmp_path):
    path = _write(tmp_path, "basics: {}\nwork: []\n")
    assert validate_resume(path) == []


def test_empty_source_rejected(tmp_path):
    assert validate_resume(_write(tmp_path, "")) == ["resume source is empty"]


def test_non_mapping_source_rejected(tmp_path):
    path = _write(tmp_path, "- a\n- b\n")
    assert "resume must be a YAML mapping" in validate_resume(path)[0]
