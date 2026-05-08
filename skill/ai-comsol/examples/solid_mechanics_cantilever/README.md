# 3D Solid Mechanics Cantilever Demo

This demo builds a 3D cantilever beam in COMSOL through the Python `mph` package.
One end is fixed and a total downward force is applied at the free end.
The script exports the model, displacement data, PNG plots, and a beam-theory verification report.

## Model

| Item | Value |
| --- | --- |
| Geometry | Rectangular beam |
| Length | `100 mm` |
| Width | `10 mm` |
| Height | `5 mm` |
| Material | Steel-like isotropic solid |
| Young's modulus | `200 GPa` |
| Poisson's ratio | `0.30` |
| Load | `Fz = -10 N` total force on free-end face |
| Study | Stationary solid mechanics |

The beam is created as a 3D block from `x = 0` to `x = L`.
The intended boundary conditions are:

- Fixed face: `x = 0`
- Loaded face: `x = L`

The initial script uses `fixed_boundary = 1` and `free_end_boundary = 6`, which should be checked in the saved MPH if a COMSOL version assigns block boundaries differently.

## Run

From PowerShell:

```powershell
python C:\Users\94836\.agents\skills\ai-comsol\examples\solid_mechanics_cantilever\run.py
```

The script uses the shared connector:

```python
from pathlib import Path
import sys
SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from comsol_client import connect_client
client = connect_client()
```

If needed, configure COMSOL before running:

```powershell
$env:COMSOL_SERVER="D:\path\to\comsolmphserver.exe"
$env:COMSOL_PORT="2036"
```

## Outputs

The demo writes to:

```text
C:\Users\<you>\comsol-scripts\results\solid_mechanics_cantilever\
```

Expected files:

| File | Purpose |
| --- | --- |
| `solid_mechanics_cantilever.mph` | Saved COMSOL model |
| `displacement_data.txt` | Exported `x y z solid.disp u v w` data |
| `displacement_magnitude.png` | Displacement magnitude cloud plot |
| `deformed_shape.png` | Deformed-shape plot |
| `verification_report.md` | Automatic beam-theory check |
| `export_notes.txt` | Records plot/export property fallbacks |

## Verification

The validation uses Euler-Bernoulli beam theory:

```text
delta = F*L^3/(3*E*I)
I = b*h^3/12
```

For this geometry:

```text
L = 0.10 m
b = 0.010 m
h = 0.005 m
E = 200e9 Pa
F = 10 N
I = 0.010*0.005^3/12 = 1.04167e-10 m^4
delta ~= 1.6e-4 m
```

The report compares the average `w` displacement on the free-end face with the theoretical value and expects a downward sign.
Because the COMSOL model is a coarse 3D continuum mesh and the check is 1D beam theory, the first-pass tolerance is 20%.

## Notes for Continuation

- If solving fails with a rigid-body or zero-displacement issue, inspect the fixed and loaded boundary IDs first.
- If PNG export fails because a plot property differs across COMSOL versions, keep the model/data/report path working and record the failed property in `export_notes.txt`.
- If the displacement quantity is exported in model units rather than SI units on a local COMSOL setup, adjust the report parser or data export unit consistently before judging the relative error.
