"""Tests for JSON Resume validation against the official schema and canonical formatting."""

import pytest

from src.format_resume import (
    RESUME_PATH,
    render_canonical_yaml,
    resume_yaml_is_canonical,
)
from src.format_resume import (
    main as format_main,
)
from src.validate_resume import main as validate_main
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


def test_committed_resume_yaml_is_canonical():
    assert resume_yaml_is_canonical(RESUME_PATH), (
        "resources/cv.yaml is not in canonical format; "
        "run `just format-resume` and commit the result."
    )


def test_canonical_preserves_anchors_and_placeholders(tmp_path):
    content = (
        "basics:\n"
        "  name: '{{ name }}'\n"
        "work:\n"
        "- &co\n"
        "  name: Acme\n"
        "  position: Senior Dev\n"
        "- <<: *co\n"
        "  position: Junior Dev\n"
    )
    path = _write(tmp_path, content)
    assert resume_yaml_is_canonical(path)
    rendered = render_canonical_yaml(content)
    assert "&co" in rendered
    assert "<<: *co" in rendered
    assert "{{ name }}" in rendered


def test_format_check_and_rewrite(tmp_path):
    drifted = 'basics:\n  name: "Jane Doe"\nwork:\n  - name: "Acme"\n    position: "Dev"\n\n'
    path = _write(tmp_path, drifted)
    assert not resume_yaml_is_canonical(path)
    assert format_main([path, "--check"]) == 1
    assert validate_main([path]) == 0
    assert validate_main([path, "--check-canonical"]) == 2

    # Rewrite in place
    assert format_main([path]) == 0
    assert resume_yaml_is_canonical(path)
    assert format_main([path, "--check"]) == 0
    assert format_main([path]) == 0
    assert validate_main([path, "--check-canonical"]) == 0


def test_validate_main_fails_on_schema_violation(tmp_path):
    path = _write(tmp_path, "basics:\n  name: X\n  email: 'not-an-email'\n")
    assert validate_main([path]) == 1
    assert validate_main([path, "--check-canonical"]) == 1


def test_render_canonical_yaml_empty_and_undefined_alias():
    import yaml

    assert render_canonical_yaml("") == ""
    with pytest.raises(yaml.composer.ComposerError):
        render_canonical_yaml("work:\n- *missing\n")
