# AgeLens V2 Environment

## Governed Runtime Record

The released Stage 4 runtime record is stored in
`results/tables/v2/18_stage4_runtime_versions.csv`.

| Component | Governed version |
| --- | --- |
| Python | 3.13.14 |
| NumPy | 2.4.6 |
| pandas | 3.0.5 |
| SciPy | 1.18.0 |
| scikit-learn | 1.9.0 |
| interpret | 0.7.8 |
| interpret-core | 0.7.8 |
| R | 4.5.1 |

## Python Installation

Create a dedicated environment and install:

```bash
python -m venv .venv-v2
python -m pip install --upgrade pip
python -m pip install -r requirements-v2.txt
```

`requirements-v2.txt` pins every core Python analytical package captured in
the governed Stage 4 runtime record. Notebook-interface packages are included
without invented historical pins because their exact versions were not
recorded in that table.

## R Environment

The governed Stage 2 and Stage 3 survey analyses use R. See `R_PACKAGES.md`
and the runtime/version records in the V2 aggregate tables. The recorded R
runtime is 4.5.1.

## Reproduction Boundary

Raw NHANES XPT files and participant-level analytic datasets are intentionally
outside the public repository. Public validators operate on released
aggregate artifacts. Full refitting requires the governed source-data setup
and does not change the released estimands or model specifications.
