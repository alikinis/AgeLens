# AgeLens public cleanup report

- Personal absolute project paths removed from current repository: yes
- Notebook source cells changed: yes, three display-only statements
- Scientific calculation cells changed: no
- Participant-level rendered notebook previews removed: 3
- Participant-level notebook-output scan: passed
- Stage 5 source-manifest hashing made line-ending independent: yes
- Repository build manifest converted to repository-relative paths: yes
- Preflight detects Windows, macOS, and Linux user-home paths: yes
- Preflight detects rendered notebook outputs containing participant identifiers: yes
- Updated preflight result: passed

Public notebook provenance is recorded in:

- `release/public_notebook_sanitization.json`
- `release/public_notebook_inventory.csv`

The V2.0.1 maintenance release closed public display hygiene,
source-manifest portability, and public-source validation defects. V2.0.2
completed the root V2 quick-start environment instructions, R dependency
documentation, the public-snapshot builder, current citation metadata, and CI
snapshot validation. V2.0.3 extends the cryptographic invariant from 79
governed configs, tables, and figures to 108 governed artifacts by adding all
14 public notebooks, four analysis scripts, and 11 V2 scientific execution
scripts. V2.0.4 aligns GitHub Actions with Python 3.13, installs the
minimal pinned validator dependencies before validation, and verifies the
CI runtime contract. Scientific calculations, estimates, aggregate
scientific tables, figures, models, notebooks, execution scripts, and
conclusions are unchanged.
