# Case Guidelines

Each ai-comsol example should be both runnable and useful as a prompt reference for future simulations.

## Required Files

Every case directory should contain:

| File | Purpose |
| --- | --- |
| `run.py` | Complete runnable COMSOL/mph workflow |
| `README.md` | Human-facing setup, physics assumptions, run command, outputs, verification |
| `PROMPT_NOTES.md` | Agent-facing notes: prompts, errors, fixes, reusable lessons |

## Required Outputs

Write runtime outputs under:

```text
C:\Users\<you>\comsol-scripts\results\<case_name>\
```

Each case should try to export:

- COMSOL model: `.mph`
- Numeric data: `.txt` or `.csv`
- Visualization: `.png`, or PNG frames / GIF for transient cases
- Verification report: `verification_report.md`

## Connection Pattern

Use the shared client helper:

```python
from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from comsol_client import connect_client  # noqa: E402

client = connect_client()
```

The helper checks `COMSOL_PORT`, checks whether the server is already listening, and starts `comsolmphserver` if needed.

## Verification Pattern

Each case should verify a physics-specific quantity instead of only checking that COMSOL solved.

Examples:

- Electrostatics: compare center-region electric field to `E = DeltaV / gap`.
- Cantilever: compare free-end displacement to Euler-Bernoulli beam theory.
- Magnetostatics: check symmetry and field decay away from the magnet.
- Transient impact demos: check fixed boundaries, peak displacement timing, and qualitative stress/deflection response.

## Prompt Notes Pattern

`PROMPT_NOTES.md` should include:

- Modeling assumptions
- COMSOL API choices
- Errors encountered and fixes
- Output files generated
- Verification result
- Reusable prompt for future agents

Keep the notes concrete and based on actual commands or observed results.
