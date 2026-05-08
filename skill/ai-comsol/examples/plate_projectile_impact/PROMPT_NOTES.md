# Prompt Notes

## User Request

Create a runnable COMSOL Python case for a steel plate impacted by a high-speed
projectile and export GIF or video-style postprocessing. If true penetration,
fracture, or perforation cannot be reliably created from scratch through the
available COMSOL API/modules, make a clear simplified model.

## Chosen Simplification

The current `run.py` uses a 2D plane-strain transient solid mechanics model with
an equivalent half-sine pressure pulse on the plate surface. This is intended to
show displacement and stress cloud plots over time.

This is explicitly not a high-fidelity ballistic penetration model.

## Implementation Notes

- Uses only the shared `connect_client()` helper from:
  `C:\Users\94836\.agents\skills\ai-comsol\scripts\comsol_client.py`
- Writes outputs to:
  `C:\Users\94836\comsol-scripts\results\plate_projectile_impact\`
- Does not modify the shared connection helper.
- Assumes simple rectangle boundary numbering:
  - left: `1`
  - top: `3`
  - right: `4`
- These IDs were verified from exported displacement data in COMSOL 6.4:
  the old `left = 4` assumption fixed the right edge instead.

## Known Follow-Up Work

- Confirm the correct COMSOL property names for:
  - transient solid inertia inclusion
  - plane strain setting
  - boundary pressure load setting
- `BoundaryLoad` with `"Pressure"` failed in COMSOL 6.4. The validated setup
  uses `LoadType = "ForceArea"` and `FperArea = ["0", "-p_pulse", "0"]`.
- Improve the load selection so only a central impact patch is loaded. The
  current handoff version loads the full top boundary for API stability.
- Add robust time-step frame export after confirming COMSOL 6.4 image export
  properties in this installation.
- COMSOL transient data export used repeated expression columns:
  `x, y, disp@t0, mises@t0, disp@t1, mises@t1, ...`.
  The report parser was updated accordingly.

## Verification Criteria

The final validated case should show:

- Maximum displacement increases during or just after the pressure pulse.
- Fixed boundary displacement remains close to zero.
- Von Mises stress and displacement are finite and smooth enough for a demo.
- Output includes `.mph`, numeric data, PNG frames or GIF/video, and
  `verification_report.md`.

Validated main-agent result:

- maximum displacement `3.366478e-4 m`
- peak-displacement time `4.0e-5 s`
- fixed left boundary displacement `0`
- one PNG frame exported
- conclusion `PASS`

Postprocessing correction:

- The first image only colored displacement on the undeformed geometry, so the plate still looked straight.
- Add a second 2D plot group with a `Deform` subfeature on the surface plot.
- The validated visual export uses `scale = 50` and writes `frames/frame_deformed_displacement.png`.

## Safety Boundary

Keep this as a material response visualization. Do not add projectile
optimization, penetration tuning, armor defeat guidance, or weapon performance
recommendations.
