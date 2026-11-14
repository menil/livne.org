# AI Decision Record: Canonical Resume YAML Formatting Enforcement

## Context & Goal
Enforce canonical YAML formatting for `cv/resources/cv.yaml` across `just validate`, `.githooks/pre-commit`, and CI checks, mirroring the approach used in the `GitEmployed` repository while preserving Jinja2 PII placeholders (`{{ name }}`, `{{ email }}`, etc.) and YAML anchors/aliases (`&whitepages`, `*whitepages`, `&fullcontact`, `*fullcontact`).

## Architecture & Key Decisions
- **AST-level PyYAML Normalization with Anchor Preservation (`cv/src/format_resume.py`)**: Instead of a standard `yaml.safe_load` + `yaml.safe_dump` round-trip (which resolves and flattens YAML anchors/merge keys), we use `yaml.compose` and `yaml.serialize` with custom `_AnchorPreservingLoader` and `_AnchorPreservingDumper` subclasses. This retains user-defined anchor names (`&whitepages`, `&fullcontact`) and `<<: *alias` merge structures while resetting scalar quoting and flow styles to PyYAML's canonical emitter defaults.
- **Validation CLI Integration (`cv/src/validate_resume.py`)**: Extended `python -m src.validate_resume` with `--check-canonical` (exiting with status `2` when schema-valid but non-canonical), matching `GitEmployed`'s validator contract.
- **Task Runner, Pre-commit, and CI (`cv/Justfile`, `.githooks/pre-commit`)**:
  - Added `format-resume` and `format-check-resume` targets to `cv/Justfile` and wired them into `format`, `check-format`, and `validate-resume`.
  - Updated `.githooks/pre-commit` to run `just validate` inside `cv/` (using `devenv shell -- just validate` when outside an active shell) in addition to the staged PII check.

## Alternatives Considered & Rejected
- **Plain `yaml.safe_load` + `yaml.safe_dump`**: Rejected because `safe_load` constructs Python dicts and expands all YAML anchors (`&whitepages`) and merge keys (`<<: *whitepages`), losing the DRY anchor structure in `cv/resources/cv.yaml`.
- **External YAML formatters (Prettier / Biome / `yamlfmt`)**: Rejected to stay consistent with `GitEmployed`'s Python-native PyYAML canonical serialization format without introducing extra formatter dependencies.
