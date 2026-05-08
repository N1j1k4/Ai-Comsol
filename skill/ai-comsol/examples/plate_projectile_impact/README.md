# Plate Projectile Impact Demo

This case demonstrates a simplified steel-plate impact response in COMSOL using
Python `mph`. It is intentionally a visualization of transient deformation and
stress after a short equivalent pressure pulse.

It is not a high-fidelity ballistic penetration, perforation, fracture, erosion,
or weapon-optimization model.

## Model

- Geometry: 2D plane-strain rectangular steel plate section
- Material: linear elastic steel
  - `E = 210 GPa`
  - `nu = 0.30`
  - `rho = 7850 kg/m^3`
- Loading: half-sine pressure pulse on the top boundary
- Constraint: left boundary fixed
- Study: transient solid mechanics, `0 us` to `40 us`

The pressure pulse is a load approximation for demonstration:

```text
p(t) = p0 sin(pi t / tp), 0 <= t <= tp
p(t) = 0, t > tp
```

The default values are:

```text
p0 = 250 MPa
tp = 8 us
```

## Run

```powershell
python C:\Users\94836\.agents\skills\ai-comsol\examples\plate_projectile_impact\run.py
```

The script uses the shared connection helper:

```python
from pathlib import Path
import sys
SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from comsol_client import connect_client
client = connect_client()
```

## Outputs

The case writes to:

```text
C:\Users\94836\comsol-scripts\results\plate_projectile_impact\
```

Expected outputs:

| File | Purpose |
| --- | --- |
| `plate_projectile_impact.mph` | Saved COMSOL model |
| `impact_data.txt` | Exported displacement and von Mises stress data |
| `frames\frame_displacement.png` | Best-effort displacement plot export |
| `animation_export_note.txt` | Written only if COMSOL image export fails |
| `verification_report.md` | Verification checklist and parsed result summary |

## Animation

The script currently performs a best-effort PNG export from the transient plot
group. COMSOL's Java image/animation export properties can vary by version, so
the handoff-safe path is:

1. Run `run.py`.
2. Open `plate_projectile_impact.mph` in COMSOL if automated frame export fails.
3. Use plot group `pg_disp` to export displacement frames over the stored time
   steps.
4. Combine frames into a GIF with a local tool such as ImageMagick:

```powershell
magick -delay 8 -loop 0 frames\frame_*.png plate_projectile_impact.gif
```

## Verification Expectations

After a successful solve, check:

- Maximum displacement is nonzero.
- Displacement grows during or shortly after the load pulse.
- The fixed left boundary has displacement near zero compared with the peak.
- The displacement magnitude is qualitatively small for an elastic steel plate
  under a microsecond-scale pressure pulse.

The generated `verification_report.md` records the current status and flags
missing data when COMSOL did not complete the solve or export.

## Safety and Scope

This example is for material-response visualization only. It does not provide
projectile design, penetration prediction, lethality estimates, or performance
optimization guidance.
