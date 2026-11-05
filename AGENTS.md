# hapax-mcp Agent Instructions

This repository is published by **Hapax Research Lab** under the `hapax-systems` GitHub organization. Do not create, move, or point repository automation outside `hapax-systems`.

## Review Guidelines

External GitHub App reviewers are advisory unless a governed task explicitly routes them into the review process.

- Keep Codecov and Semgrep as advisory signal sources unless a governed task promotes a specific aggregate check.
- Preserve the `all-green` aggregate check in `.github/workflows/ci.yml` for branch ruleset compliance.
- Never print or persist plaintext secrets; resolve credentials through the deployment secret store or GitHub Secrets.
- Verify `ruff check`, `ruff format --check`, `pyright`, and `pytest` locally before opening or updating a pull request.
