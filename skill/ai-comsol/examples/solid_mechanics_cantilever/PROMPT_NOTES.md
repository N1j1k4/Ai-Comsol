# Prompt Notes: Solid Mechanics Cantilever

## User Request

Create an `ai-comsol` example for a cantilever beam:

- One end fixed
- Free end loaded by a force
- Export a deformed-shape image
- Export a displacement magnitude cloud image
- Save `.mph`, displacement data, at least one PNG, and `verification_report.md`
- Verify free-end displacement order of magnitude with `delta = F*L^3/(3*E*I)`
- Use the shared `scripts/comsol_client.py` connection helper

## Implementation Choices

- Case path: `C:\Users\94836\.agents\skills\ai-comsol\examples\solid_mechanics_cantilever\`
- Result path: `C:\Users\94836\comsol-scripts\results\solid_mechanics_cantilever\`
- Geometry: 3D rectangular block, `L = 100 mm`, `b = 10 mm`, `h = 5 mm`
- Material: isotropic steel-like material, `E = 200 GPa`, `nu = 0.30`, `rho = 7850 kg/m^3`
- Load: total force `Fz = -10 N` on free-end face
- Study: stationary solid mechanics
- Mesh: automatic tetrahedral mesh, `hauto = 4`

The selected beam theory moment of inertia is:

```text
I = b*h^3/12
```

The force is in the z direction, so the rectangular cross-section bends about the y axis.
Using SI units:

```text
I = 0.010*0.005^3/12 = 1.04167e-10 m^4
delta = 10*0.10^3/(3*200e9*1.04167e-10) ~= 1.6e-4 m
```

## COMSOL API Assumptions to Verify

The current `run.py` assumes the block boundary IDs are:

- `fixed_boundary = 1` for `x = 0`
- `free_end_boundary = 6` for `x = L`

This is the main item for the next agent to verify in COMSOL.
If the solution gives zero displacement, wrong sign, or a rigid-body error, inspect and update those two IDs.

The boundary load is set with:

```python
c.physics("solid").feature("bndl1").set("LoadType", "TotalForce")
c.physics("solid").feature("bndl1").set("Ftot", ["0", "0", "Fz"])
```

If a COMSOL build uses different property names, the smallest change is to switch to force-per-area traction on the free-end boundary and keep the same total force magnitude by dividing by `b*h`.

## Plot/Export Fallback Policy

`run.py` attempts two 3D image exports:

- `displacement_magnitude.png`
- `deformed_shape.png`

The image export helper records property failures in `export_notes.txt` instead of changing the model.
If image export fails fully on a headless server, keep `.mph`, data, and report generation intact, then document the COMSOL plot/export error in `verification_report.md` or `export_notes.txt`.

## Current Status

Validated by the main agent in COMSOL 6.4.

Fixes made during validation:

- `set("hauto", 4)` caused a JPype overload ambiguity. Use string values such as `set("hauto", "4")`.
- Parameter name `h` conflicted with a COMSOL internal/global variable during equation compilation. Use explicit names such as `beam_h`.
- COMSOL exported coordinates and displacement in `mm` because the geometry unit was `mm`. Convert `x`, `y`, `z`, `solid.disp`, `u`, `v`, `w` to meters before comparing with beam theory.
- A displacement cloud plot alone can look visually straight because the true deflection is small relative to geometry. Add a `Deform` plot subfeature and use an explicit visual scale. The validated deformed-shape export uses `scale = 100`.

Validated result:

- free-end average `w = -1.5803e-4 m`
- beam-theory displacement `1.6e-4 m`
- relative error `1.231%`
- conclusion `PASS`
