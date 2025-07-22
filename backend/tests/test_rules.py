"""
Unit‑tests for Mini‑Entangl rule engine.
Run with:  pytest -q
"""

import pytest
from ..main import (
    parse_steps,
    analyze_steps,
    apply_fixes,
    find_duplicate_issues,
)

# ---------- helpers ----------
def _md(*lines: str) -> str:
    """Join lines with newlines for readability."""
    return "\n".join(lines)


# ---------- tests ----------
def test_shutdown_before_backup_detected():
    md = _md(
        "1. Shut down mains",
        "2. Start backup generator",
    )
    steps = parse_steps(md)
    issues = analyze_steps(steps)
    assert any("Power shutdown occurs before backup" in i.description for i in issues)
    assert issues[0].step_number == 1


def test_apply_fixes_reorders_steps():
    md = _md(
        "1. Shut down mains",
        "2. Start backup generator",
    )
    steps = parse_steps(md)
    issues = analyze_steps(steps)
    fixed = apply_fixes(steps, issues)
    assert fixed[0].raw.lower().startswith("start backup"), "Backup step should be first"


def test_no_issue_when_order_is_safe():
    md = _md(
        "1. Start backup generator",
        "2. Shut down mains",
    )
    steps = parse_steps(md)
    issues = analyze_steps(steps)
    assert len(issues) == 0


def test_semantic_duplicate_detection():
    md = _md(
        "1. Shut down mains",
        "2. Kill main feed",  # semantic duplicate
        "3. Start backup generator",
    )
    steps = parse_steps(md)
    dup_issues = find_duplicate_issues(steps, threshold=0.5)
    assert any("Duplicate of step 1" in i.description for i in dup_issues)
