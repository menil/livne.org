#!/usr/bin/env python3
"""Shared JSON Resume model for the resume builders.

Loads a JSON Resume YAML source, renders PII placeholders, and prepares a
structure matching the legacy resume model consumed by the MD, HTML, PDF and
DOCX templates. Roles at the same company are grouped into company blocks,
and positions that ended more than 10 years ago are split into "earlier
career" entries.
"""

from __future__ import annotations

from datetime import date
from typing import Any, cast

import yaml

from src.common import apply_config, load_config

EARLY_CAREER_YEARS = 10


def _linkedin(basics: dict[str, Any]) -> str:
    """Return the LinkedIn profile URL, if any, from the basics profiles."""
    for profile in basics.get("profiles", []):
        if str(profile.get("network", "")).lower() == "linkedin":
            return str(profile.get("url", ""))
    return ""


def _end_year(entry: dict[str, Any]) -> int | None:
    """Extract the ending year of a work entry, or None if it has no end date."""
    end = entry.get("endDate")
    if not end:
        return None
    try:
        return int(str(end)[:4])
    except ValueError:
        return None


def _format_dates(start: str | None, end: str | None) -> str:
    """Format a work entry's dates into the display range (e.g. 2020-2026)."""
    if start and end:
        return f"{start}-{end}"
    if end:
        return end
    if start:
        return f"{start}-Present"
    return ""


def _group_work(work: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Group consecutive work entries with the same company name."""
    groups: list[dict[str, Any]] = []
    for entry in work or []:
        if groups and groups[-1]["name"] == entry["name"]:
            groups[-1]["roles"].append(entry)
        else:
            groups.append(
                {
                    "name": entry["name"],
                    "description": entry.get("description", ""),
                    "roles": [entry],
                }
            )
    return groups


def _prepare_company(group: dict[str, Any]) -> dict[str, Any]:
    """Convert a company group into the legacy company shape for templates."""
    return {
        "name": group["name"],
        "description": group["description"],
        "roles": [
            {
                "position": role.get("position", ""),
                "dates": _format_dates(role.get("startDate"), role.get("endDate")),
                "highlights": role.get("highlights", []),
            }
            for role in group["roles"]
        ],
    }


def prepare(data: dict[str, Any], as_of: date | None = None) -> dict[str, Any]:
    """Convert JSON Resume data into the legacy shape consumed by the templates."""
    as_of = as_of or date.today()
    threshold_year = as_of.year - EARLY_CAREER_YEARS

    companies: list[dict[str, Any]] = []
    early_career: list[dict[str, Any]] = []
    for group in _group_work(data.get("work")):
        end_years = [_end_year(role) for role in group["roles"]]
        is_early = bool(end_years) and all(
            year is not None and year < threshold_year for year in end_years
        )
        company = _prepare_company(group)
        (early_career if is_early else companies).append(company)

    basics = dict(data.get("basics", {}))
    basics["linkedin"] = _linkedin(basics)

    return {
        "basics": basics,
        "work": companies,
        "early_career": [
            {
                "dates": role["dates"],
                "details": f"{role['position']}, {company['name']}",
            }
            for company in early_career
            for role in company["roles"]
        ],
        "skills": data.get("skills", []),
        "education": data.get("education", []),
    }


def load_data(yaml_file: str) -> dict[str, Any]:
    """Load a JSON Resume YAML file and render its PII placeholders."""
    config = load_config(yaml_file)
    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = f.read()
    return cast("dict[str, Any]", yaml.safe_load(apply_config(yaml_content, config)))


def load_resume(yaml_file: str, as_of: date | None = None) -> dict[str, Any]:
    """Load, render placeholders, and prepare a JSON Resume YAML file."""
    return prepare(load_data(yaml_file), as_of=as_of)
