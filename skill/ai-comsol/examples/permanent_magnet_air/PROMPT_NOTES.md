# Prompt Notes

## Worker Scope

Worker 2 owns only:

```text
C:\Users\94836\.agents\skills\ai-comsol\examples\permanent_magnet_air\
```

The shared connection helper is read-only:

```text
C:\Users\94836\.agents\skills\ai-comsol\scripts\comsol_client.py
```

## Modeling Intent

Build a COMSOL Python/mph example for a permanent magnet in an air domain and export magnetic-field postprocessing.

Preferred physics:

- COMSOL AC/DC
- Magnetic Fields / No Currents
- axially magnetized permanent magnet
- stationary study

If the COMSOL API or license is unstable, the script must record the limitation and provide a runnable alternative.

## Dissipation Clarification

The original wording included "耗散". For this model, static magnetostatics is not a dissipation problem. The report should explain this and provide physically meaningful outputs instead:

- `B`
- `H`
- magnetic energy density
- field decay in air

## Output Contract

Write results to:

```text
C:\Users\94836\comsol-scripts\results\permanent_magnet_air\
```

Required artifacts:

- model `.mph` when COMSOL succeeds, otherwise a marker explaining why it was not created
- magnetic-field data
- at least one PNG postprocessing image
- `verification_report.md`

## Verification Contract

Verify:

- axial `B` decays with distance
- symmetry across the magnet center plane
- order of magnitude is plausible for a 1.2 T remanence cylindrical magnet

## Main-Agent Validation Notes

The script ran successfully but used the analytic fallback, not a COMSOL AC/DC solve.

Observed COMSOL 6.4 interface probing:

- `MagneticFieldsNoCurrents`: unavailable
- `MagneticFields`: unavailable
- `Magnetostatics`: unavailable
- `InductionCurrents`: available
- `RotatingMachineryMagnetic`: available

Validated fallback result:

- center axial `Bz = 0.848528 T`
- `Bz` decays monotonically from 20 mm to 80 mm
- symmetry error around the magnet center plane is near machine precision
- conclusion `PASS`

Follow-up prompt for the next agent:

```text
Upgrade permanent_magnet_air from analytic fallback to a true COMSOL model using the locally available `InductionCurrents` or `RotatingMachineryMagnetic` interface. Probe supported feature names for permanent magnet/remanent flux density, then export B-field PNG and keep the analytic fallback as verification.
```
