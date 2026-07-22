from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def without_revision_history(text: str) -> str:
    return re.sub(
        r"## Revision History.*?\n---\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.repository).resolve()
    files = {
        "replication": root / "docs/governed/Replication_Protocol.md",
        "validation": root / "docs/governed/Validation_Protocol.md",
        "harmonization": root / "docs/governed/NHANES_Harmonization_Report.md",
        "decision": root / "docs/governance/Decision_Log.md",
        "gaps": root / "docs/governance/Evidence_Gap_Register.md",
    }

    errors: list[str] = []
    current: dict[str, str] = {}

    for label, path in files.items():
        if not path.exists():
            errors.append(f"Missing governance file: {path}")
            continue
        current[label] = without_revision_history(
            path.read_text(encoding="utf-8")
        )

    forbidden = {
        "provisional choice pending empirical resolution":
            "D-010 is approved",
        "Final release remains disabled":
            "D-017 approved final release",
        "not yet written) Validation Report":
            "validation is complete",
        "NHANES-III training bias: unresolved":
            "D-012 closed EG-004",
        "## 9. Remaining Open Items":
            "V1 harmonization is complete",
        "All three open gaps (EG-004, EG-010, EG-014)":
            "those gaps are closed",
        "highest magnitude of any open gap":
            "EG-014 is closed as an accepted limitation",
        "Open - flagged for re-verification":
            "EG-012 is closed",
    }

    for label, text in current.items():
        for phrase, reason in forbidden.items():
            if phrase in text:
                errors.append(
                    f"{label}: stale phrase {phrase!r} ({reason})"
                )

    required = {
        "replication": [
            "D-010; EG-010 closed",
            "D-011; EG-014 closed",
            "D-012; EG-004 closed",
            "D-017 approved",
        ],
        "validation": [
            "Acceptance criterion (D-013)",
            "No validation or release gate remains open",
        ],
        "harmonization": [
            "Final disposition (D-012; EG-004 closed",
            "No Core harmonization Evidence Gap remains open",
        ],
        "decision": [
            "No Core Evidence Gap remains open for D-001",
        ],
        "gaps": [
            "closed under D-010",
            "closed under D-011",
            "closed under D-012",
            "Closed — documented wording ambiguity",
        ],
    }

    for label, phrases in required.items():
        text = current.get(label, "")
        for phrase in phrases:
            if phrase not in text:
                errors.append(
                    f"{label}: required phrase missing: {phrase!r}"
                )

    gap_text = current.get("gaps", "")
    statuses = re.findall(
        r"\|\s*Review Status\s*\|\s*(.*?)\s*\|",
        gap_text,
        flags=re.IGNORECASE,
    )

    if len(statuses) != 14:
        errors.append(
            "gaps: expected 14 operative Review Status rows, "
            f"found {len(statuses)}"
        )

    for status in statuses:
        cleaned = re.sub(r"[*_`]", "", status).strip().lower()
        if not cleaned.startswith("closed"):
            errors.append(
                "gaps: operative Review Status is not closed: "
                f"{status.strip()!r}"
            )

    if errors:
        print("GOVERNANCE CONSISTENCY FAILED")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("GOVERNANCE CONSISTENCY PASSED")
    print(
        "All 14 V1 Evidence Gaps are dispositioned; "
        "EG-004, EG-010, EG-012, and EG-014 are current."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
