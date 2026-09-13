import json

import pytest

from src.export_json import export_json, main
from tests.conftest import DUMMY_EMAIL, DUMMY_NAME, DUMMY_PHONE, SAMPLE_YAML


def test_export_json_happy_path(tmp_path, monkeypatch):
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(SAMPLE_YAML)
    json_file = tmp_path / "dist" / "resume.json"

    monkeypatch.setenv("RESUME_NAME", DUMMY_NAME)
    monkeypatch.setenv("RESUME_EMAIL", DUMMY_EMAIL)
    monkeypatch.setenv("RESUME_PHONE", DUMMY_PHONE)

    export_json(str(yaml_file), str(json_file), public=False)

    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert data["basics"]["name"] == DUMMY_NAME
    assert data["basics"]["email"] == DUMMY_EMAIL
    assert data["basics"]["phone"] == DUMMY_PHONE


def test_export_json_public(tmp_path, monkeypatch):
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(SAMPLE_YAML)
    json_file = tmp_path / "dist" / "resume_public.json"

    monkeypatch.setenv("RESUME_NAME", DUMMY_NAME)
    monkeypatch.setenv("RESUME_EMAIL", DUMMY_EMAIL)
    monkeypatch.setenv("RESUME_PHONE", DUMMY_PHONE)

    export_json(str(yaml_file), str(json_file), public=True)

    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert data["basics"]["name"] == DUMMY_NAME
    assert data["basics"]["email"] == DUMMY_EMAIL
    assert "phone" not in data["basics"]


def test_export_json_no_config(tmp_path, monkeypatch):
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(SAMPLE_YAML)
    json_file = tmp_path / "resume.json"

    for var in ["RESUME_NAME", "RESUME_EMAIL", "RESUME_PHONE", "RESUME_LINKEDIN", "RESUME_GITHUB"]:
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(ValueError, match="no PII config found"):
        export_json(str(yaml_file), str(json_file))


def test_main_cli_happy_path(tmp_path, monkeypatch):
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(SAMPLE_YAML)
    json_file = tmp_path / "resume.json"

    monkeypatch.setenv("RESUME_NAME", DUMMY_NAME)
    monkeypatch.setenv("RESUME_EMAIL", DUMMY_EMAIL)
    monkeypatch.setattr("sys.argv", ["export_json.py", str(yaml_file), str(json_file), "--public"])

    main()

    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert "phone" not in data["basics"]


def test_main_cli_error(tmp_path, monkeypatch):
    yaml_file = tmp_path / "cv.yaml"
    yaml_file.write_text(SAMPLE_YAML)
    json_file = tmp_path / "resume.json"

    for var in ["RESUME_NAME", "RESUME_EMAIL", "RESUME_PHONE", "RESUME_LINKEDIN", "RESUME_GITHUB"]:
        monkeypatch.delenv(var, raising=False)

    monkeypatch.setattr("sys.argv", ["export_json.py", str(yaml_file), str(json_file)])

    with pytest.raises(SystemExit):
        main()
