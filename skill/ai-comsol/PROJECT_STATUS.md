# ai-comsol Project Status

Last updated: 2026-05-08

This file is the handoff snapshot for continuing the `ai-comsol` project in a new chat.
Start future sessions by reading this file, then inspect the linked files as needed.

## Project Goal

Build `ai-comsol` into a useful open-source COMSOL automation project:

- Use Python `mph` to drive COMSOL 6.4.
- Generate reproducible simulation cases.
- Export models, data, plots, and verification reports.
- Preserve practical COMSOL API lessons so future AI agents avoid repeating mistakes.

The long-term goal is a GitHub-ready project with strong demos, documentation, and reliable workflows.

## Important Local Paths

Skill/project root:

```text
C:\Users\94836\.agents\skills\ai-comsol\
```

Runtime outputs:

```text
C:\Users\94836\comsol-scripts\results\
```

Shared COMSOL connection helper:

```text
C:\Users\94836\.agents\skills\ai-comsol\scripts\comsol_client.py
```

COMSOL server path used on this machine:

```text
D:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolmphserver.exe
```

Default COMSOL server port:

```text
2036
```

## Environment Notes

- Python works from the user's normal PowerShell as `python`.
- `mph` is installed for Python 3.13.
- Direct `mph.Client(cores=1)` standalone mode caused startup/license/native-library problems.
- Server mode works:

```powershell
comsolmphserver.exe -port 2036
python -c "import mph; client=mph.Client(port=2036); print('connected')"
```

- `scripts/comsol_client.py` now checks port `2036`; if no server is listening, it starts `comsolmphserver.exe` automatically in a new console.

## Files Changed Today

### Core skill/reference files

- `SKILL.md` was inspected but not deeply rewritten.
- `references/comsol-api.md`
  - Replaced a corrupted/garbled file.
  - Added clean COMSOL/mph recipes.
  - Added 2D plot group and PNG image export notes.

### Shared helper

- `scripts/comsol_client.py`
  - New shared helper.
  - Provides `connect_client()`.
  - Starts `comsolmphserver` if needed.
  - Reads `COMSOL_PORT` and `COMSOL_SERVER` environment variables.

### Existing template

- `scripts/template_2d_es.py`
  - Updated to use server connection.
  - Added electric-field PNG export.

### Case guidelines

- `examples/CASE_GUIDELINES.md`
  - New standard for each example.
  - Required files: `run.py`, `README.md`, `PROMPT_NOTES.md`.
  - Required outputs: `.mph`, data, PNG/frames, `verification_report.md`.

## Completed Cases

### 1. 2D Parallel-Plate Electrostatics

Case path:

```text
C:\Users\94836\.agents\skills\ai-comsol\examples\electrostatics_2d_parallel_plate\
```

Main file:

```text
run.py
```

Outputs:

```text
C:\Users\94836\comsol-scripts\results\electrostatics_2d_parallel_plate\
```

Generated:

- `field_data.txt`
- `electric_field.png`
- `parallel_plate_2d.mph`
- `verification_report.md`

Validated result:

- `V min = -1000 V`
- `V max = 1000 V`
- `Global E max ≈ 4.35e5 V/m`
- `Center-region E avg ≈ 2.222e5 V/m`
- `Theory center E ≈ 2.222e5 V/m`
- Conclusion: `PASS`

Important lesson:

- Do not verify ideal parallel-plate field using global `E_max`; edge/corner fields are higher.
- Use central gap average field.
- Actual inner electrode gap is `0.9 cm`, not nominal `1 cm`, because electrode thickness is `gap/10`.

### 2. Solid Mechanics Cantilever

Case path:

```text
C:\Users\94836\.agents\skills\ai-comsol\examples\solid_mechanics_cantilever\
```

Outputs:

```text
C:\Users\94836\comsol-scripts\results\solid_mechanics_cantilever\
```

Generated:

- `displacement_data.txt`
- `displacement_magnitude.png`
- `deformed_shape.png`
- `solid_mechanics_cantilever.mph`
- `verification_report.md`

Validated result:

- Beam: `L = 0.1 m`, `b = 0.01 m`, `h = 0.005 m`
- Load: `Fz = -10 N`
- Free-end average `w = -1.5803e-4 m`
- Beam-theory displacement `1.6e-4 m`
- Relative error `1.231%`
- Conclusion: `PASS`

Important lessons:

- `set("hauto", 4)` caused JPype overload ambiguity; use `set("hauto", "4")`.
- Avoid parameter name `h`; it conflicted with COMSOL internals. Use `beam_h`.
- COMSOL exported displacement in `mm`; convert to SI meters before verification.
- A displacement cloud plot can still look straight. Use a `Deform` plot subfeature and visual scale.
- Current deformed shape uses `scale = 100`.

### 3. Permanent Magnet in Air

Case path:

```text
C:\Users\94836\.agents\skills\ai-comsol\examples\permanent_magnet_air\
```

Outputs:

```text
C:\Users\94836\comsol-scripts\results\permanent_magnet_air\
```

Generated:

- `magnetic_field_data.csv`
- `axis_Bz_decay.csv`
- `magnetic_flux_density.png`
- `permanent_magnet_air.mph`
- `verification_report.md`

Validated result:

- Execution mode: `COMSOL Magnetic Fields (mf / InductionCurrents)`
- Conclusion: `PASS`

Important COMSOL API mapping:

- GUI physics: AC/DC > Magnetic Fields, tag `mf`
- Python API creation:

```python
c.physics().create("mf", "InductionCurrents", "geom1")
```

- Permanent magnet feature:

```python
c.physics("mf").feature().create("mag1", "Magnet", 2)
```

- Important magnet settings:

```python
mag.set("ConstitutiveRelationBH", "RemanentFluxDensity")
mag.set("mur_crel_BH_RemanentFluxDensity_mat", "userdef")
mag.set("mur_crel_BH_RemanentFluxDensity", "mur_mag")
mag.set("normBr_crel_BH_RemanentFluxDensity_mat", "userdef")
mag.set("normBr_crel_BH_RemanentFluxDensity", "Br_mag")
mag.set("DirectionMethod", "UserDefined")
mag.set("directionInput", ["0", "1", "0"])
mag.set("sigma", "0[S/m]")
```

Material also needed:

```python
mat.propertyGroup("def").set("electricconductivity", "0[S/m]")
mat.propertyGroup("def").set("normBr", "Br_mag")
```

Clarification:

- Static permanent-magnet fields are not dissipative by themselves.
- Meaningful outputs: `B`, `H`, magnetic energy density, and field decay in air.

Remaining issue:

- The current COMSOL magnetic-field plot is real, but visually weak because the color scale/plot style is poor.
- Improve with field lines, local zoom, log scale, or an axial `Bz` curve.

### 4. Simplified Steel Plate Impact

Case path:

```text
C:\Users\94836\.agents\skills\ai-comsol\examples\plate_projectile_impact\
```

Outputs:

```text
C:\Users\94836\comsol-scripts\results\plate_projectile_impact\
```

Generated:

- `impact_data.txt`
- `frames/frame_displacement.png`
- `frames/frame_deformed_displacement.png`
- `plate_projectile_impact.mph`
- `verification_report.md`

Validated result:

- Maximum displacement `3.366478e-4 m`
- Peak displacement time `4.0e-5 s`
- Fixed left boundary displacement `0`
- Conclusion: `PASS`

Scope:

- This is a simplified transient solid-mechanics impact deformation demo.
- It is not a penetration/fracture/erosion/contact/ballistic performance model.

Important lessons:

- COMSOL 6.4 `BoundaryLoad` did not accept `"Pressure"`.
- Use:

```python
LoadType = "ForceArea"
FperArea = ["0", "-p_pulse", "0"]
```

- Even in 2D, `FperArea` required a 3-component vector.
- Rectangle boundary IDs were verified from displacement data:
  - `1 left`
  - `3 top`
  - `4 right`
- COMSOL transient export format was:

```text
x, y, disp@t0, mises@t0, disp@t1, mises@t1, ...
```

- The first plot only showed color on undeformed geometry; add `Deform`.
- Current deformed impact image uses `scale = 50`.

## Current Project State

The project now has:

- A working COMSOL server connection helper.
- Four example cases.
- Three true COMSOL-solved examples:
  - electrostatics
  - solid mechanics cantilever
  - permanent magnet in air
  - simplified transient impact
- Automatic output folders and verification reports.
- `PROMPT_NOTES.md` files storing lessons for future agents.

## Recommended Next Steps

### Immediate next step

Improve permanent magnet visualization:

- Add magnetic field lines or streamlines.
- Export a better `B` field image with visible gradients.
- Add axial `Bz(z)` curve image from `axis_Bz_decay.csv`.
- Possibly add local zoom near the magnet.

### Then

Create a root project README:

```text
C:\Users\94836\.agents\skills\ai-comsol\README.md
```

It should explain:

- What ai-comsol is.
- Requirements.
- How to run each case.
- Which cases are validated.
- Limitations.
- Screenshots from outputs.

### After that

Prepare GitHub-ready structure:

```text
ai-comsol/
  README.md
  skills/
  scripts/
  examples/
  docs/
```

Current installed skill path may not be ideal as a GitHub repo root; consider copying the developed project into a clean repo directory later.

## Good First Command For Future Sessions

Ask the next assistant to start with:

```text
Read C:\Users\94836\.agents\skills\ai-comsol\PROJECT_STATUS.md and continue from the recommended next steps.
```

Then inspect:

```text
C:\Users\94836\.agents\skills\ai-comsol\examples\permanent_magnet_air\run.py
C:\Users\94836\comsol-scripts\results\permanent_magnet_air\verification_report.md
```

## Safety / Scope Notes

- Do not attempt to bypass COMSOL licensing.
- For impact/projectile examples, keep the scope as material response visualization.
- Do not add projectile optimization, armor defeat guidance, or weapon performance recommendations.
- High-fidelity penetration/fracture requires explicit dynamics, contact, nonlinear material models, damage/erosion, and careful validation; current demo is not that.
