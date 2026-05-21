# ─── Lint ───────────────────────────────────────────────────
lint:
    ruff check cv/
    shellcheck .githooks/commit-msg

# ─── Format ─────────────────────────────────────────────────
format:
    ruff format cv/
    shfmt -w .githooks/commit-msg cv/.envrc

check-format:
    ruff format --check cv/
    shfmt -d .githooks/commit-msg cv/.envrc

# ─── Validate (lint + check format) ─────────────────────────
validate: lint check-format
