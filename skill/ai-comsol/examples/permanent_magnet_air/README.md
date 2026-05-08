# Permanent Magnet in Air

This example models a cylindrical permanent magnet placed in an air domain and exports the static magnetic-field distribution.

The preferred path is COMSOL AC/DC `Magnetic Fields, No Currents` with an axially magnetized permanent-magnet domain. Because COMSOL Java API tags for this interface can vary by installation/license, `run.py` includes a deterministic analytic fallback that still writes field data, a PNG plot, and a verification report.

## Run

```powershell
cd C:\Users\94836\.agents\skills\ai-comsol\examples\permanent_magnet_air
python run.py
```

If Python is not on `PATH`, run the script with the same Python environment that has `mph` installed.

## Outputs

All outputs are written to:

```text
C:\Users\94836\comsol-scripts\results\permanent_magnet_air\
```

Expected files:

- `permanent_magnet_air.mph`
- `magnetic_field_data.csv`
- `axis_Bz_decay.csv`
- `magnetic_flux_density.png`
- `verification_report.md`

If COMSOL cannot be reached or the AC/DC magnetic API differs on the machine, `permanent_magnet_air.mph` is replaced by a small text marker and the report records the limitation.

## Physical Note About "Dissipation"

The user request mentioned "dissipation". A stationary permanent magnet in air is not, by itself, a dissipative problem. With no currents, no time variation, and no magnetic loss model, there is no Joule heating or hysteresis loss to compute.

The meaningful static outputs are:

- magnetic flux density `B`
- magnetic field strength `H`
- magnetic energy density in air
- decay of the field away from the magnet

## Verification

The script checks:

- axial `Bz` decreases with increasing distance from the magnet
- `Bz(+z)` and `Bz(-z)` are symmetric
- center-field magnitude is reasonable for a 1.2 T remanence magnet

The fallback verification uses the closed-form axial field of a uniformly magnetized finite cylinder.
