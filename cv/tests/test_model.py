"""Tests for the shared JSON Resume model preparation logic."""

from datetime import date

from src import resume_model

PINNED = date(2026, 1, 1)

SAMPLE = {
    "basics": {
        "name": "Jane Doe",
        "profiles": [{"network": "LinkedIn", "url": "https://linkedin.com/in/jane"}],
    },
    "work": [
        {
            "name": "Acme",
            "description": "A widget company.",
            "position": "Senior Engineer",
            "startDate": 2021,
            "endDate": 2026,
            "highlights": ["Led the platform rewrite"],
        },
        {
            "name": "Acme",
            "description": "A widget company.",
            "position": "Junior Engineer",
            "startDate": 2019,
            "endDate": 2021,
            "highlights": [],
        },
        {"name": "OldCo", "position": "Developer", "startDate": 2005, "endDate": 2008},
    ],
    "skills": [{"name": "Languages", "keywords": ["Python"]}],
    "education": [{"studyType": "B.Sc.", "area": "Computer Science", "institution": "University"}],
}


def test_groups_same_company_entries():
    prepared = resume_model.prepare(SAMPLE, as_of=PINNED)
    assert [c["name"] for c in prepared["work"]] == ["Acme"]
    acme = prepared["work"][0]
    assert [r["position"] for r in acme["roles"]] == ["Senior Engineer", "Junior Engineer"]
    assert acme["description"] == "A widget company."
    assert acme["roles"][0]["highlights"] == ["Led the platform rewrite"]


def test_early_career_split():
    prepared = resume_model.prepare(SAMPLE, as_of=PINNED)
    assert prepared["early_career"] == [{"dates": "2005-2008", "details": "Developer, OldCo"}]


def test_early_career_shows_all_roles():
    data = {
        "work": [
            {"name": "OldCo", "position": "Senior Dev", "startDate": 2003, "endDate": 2008},
            {"name": "OldCo", "position": "Junior Dev", "startDate": 2000, "endDate": 2003},
        ]
    }
    prepared = resume_model.prepare(data, as_of=PINNED)
    assert prepared["early_career"] == [
        {"dates": "2003-2008", "details": "Senior Dev, OldCo"},
        {"dates": "2000-2003", "details": "Junior Dev, OldCo"},
    ]


def test_early_career_boundary_stays_professional():
    data = {
        "work": [
            {"name": "Co", "position": "Dev", "startDate": 2000, "endDate": 2016},
        ]
    }
    prepared = resume_model.prepare(data, as_of=PINNED)
    assert [c["name"] for c in prepared["work"]] == ["Co"]
    assert prepared["early_career"] == []


def test_open_ended_role_is_not_early_career():
    data = {"work": [{"name": "Co", "position": "Dev", "startDate": 2005}]}
    prepared = resume_model.prepare(data, as_of=PINNED)
    assert [c["name"] for c in prepared["work"]] == ["Co"]
    assert prepared["work"][0]["roles"][0]["dates"] == "2005-Present"
    assert prepared["early_career"] == []


def test_format_dates_variants():
    assert resume_model._format_dates("2020", "2026") == "2020-2026"
    assert resume_model._format_dates(None, "2026") == "2026"
    assert resume_model._format_dates("2020", None) == "2020-Present"
    assert resume_model._format_dates(None, None) == ""


def test_linkedin_from_profiles():
    prepared = resume_model.prepare(SAMPLE, as_of=PINNED)
    assert prepared["basics"]["linkedin"] == "https://linkedin.com/in/jane"


def test_linkedin_empty_without_profiles():
    data = {"basics": {"name": "Jane"}, "work": []}
    prepared = resume_model.prepare(data, as_of=PINNED)
    assert prepared["basics"]["linkedin"] == ""


def test_end_year_invalid_is_none():
    assert resume_model._end_year({"endDate": "not-a-date"}) is None
    assert resume_model._end_year({"endDate": 2005}) == 2005


def test_prepare_handles_null_work():
    prepared = resume_model.prepare({"basics": {"name": "Jane"}, "work": None}, as_of=PINNED)
    assert prepared["work"] == []
    assert prepared["early_career"] == []


def test_prepare_handles_missing_work():
    prepared = resume_model.prepare({"basics": {"name": "Jane"}}, as_of=PINNED)
    assert prepared["work"] == []
    assert prepared["early_career"] == []


def test_load_data_renders_placeholders(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUME_NAME", "Jane Doe")
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(
        "basics:\n"
        "  name: '{{ name }}'\n"
        "work:\n"
        "  - name: Co\n"
        "    position: Dev\n"
        "    startDate: 2020\n"
    )
    data = resume_model.load_data(str(yaml_file))
    assert data["basics"]["name"] == "Jane Doe"


def test_load_resume_prepares(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUME_NAME", "Jane Doe")
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(
        "basics:\n"
        "  name: '{{ name }}'\n"
        "work:\n"
        "  - name: Co\n"
        "    position: Dev\n"
        "    startDate: 2020\n"
    )
    prepared = resume_model.load_resume(str(yaml_file), as_of=PINNED)
    assert prepared["basics"]["name"] == "Jane Doe"
    assert prepared["work"][0]["roles"][0]["dates"] == "2020-Present"
