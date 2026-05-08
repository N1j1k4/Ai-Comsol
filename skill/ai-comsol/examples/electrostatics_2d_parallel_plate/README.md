# 2D Parallel-Plate Electrostatics Demo

This demo builds and solves a 2D parallel-plate electrostatics model in COMSOL through the Python `mph` package.
It exports field data, a COMSOL model file, a PNG electric-field plot, and a verification report.

## What This Demo Checks

The model has two rectangular electrodes in an air domain:

- Top electrode: `+1000 V`
- Bottom electrode: `-1000 V`
- Nominal gap parameter: `1 cm`
- Electrode thickness: `gap / 10`

Because each electrode has thickness `0.1 cm`, the actual inner distance between the electrode faces is `0.9 cm`.
The expected center-gap electric field is therefore:

```text
E = 2000 V / 0.009 m = 222222 V/m
```

The verification report compares this theoretical value with the average electric field in the central gap region.

## Requirements

- COMSOL Multiphysics 6.4
- Python with `mph` installed
- A COMSOL license that can run `comsolmphserver`

Install Python dependency:

```powershell
python -m pip install mph
```

## Run

From PowerShell:

```powershell
python C:\Users\94836\.agents\skills\ai-comsol\examples\electrostatics_2d_parallel_plate\run.py
```

The script checks whether a COMSOL mph server is listening on port `2036`.
If not, it starts:

```powershell
D:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolmphserver.exe -port 2036
```

If your COMSOL server path or port is different, set:

```powershell
$env:COMSOL_SERVER="D:\path\to\comsolmphserver.exe"
$env:COMSOL_PORT="2036"
```

## Outputs

The demo writes files to:

```text
C:\Users\<you>\comsol-scripts\results\electrostatics_2d_parallel_plate\
```

Expected files:

| File | Purpose |
| --- | --- |
| `field_data.txt` | Exported numeric field data: `x`, `y`, `V`, `es.normE`, `es.Ex`, `es.Ey` |
| `electric_field.png` | 2D electric-field magnitude plot |
| `parallel_plate_2d.mph` | Saved COMSOL model |
| `verification_report.md` | Automatic numerical verification |

## Verification Logic

Do not verify this case with the global maximum electric field.
The maximum field occurs near electrode edges and corners because of fringe-field enhancement.

Instead, the demo verifies the central gap:

```text
abs(x) < 1.0 cm
abs(y) < 0.25 cm
```

The report passes when:

- Voltage range is approximately `[-1000 V, 1000 V]`
- Center-region average electric field is within 5% of the theoretical center field

Typical result:

```text
V min: -1000 V
V max: 1000 V
Global E max: ~4.35e5 V/m
Center-region E avg: ~2.22e5 V/m
Theory center E: ~2.22e5 V/m
Conclusion: PASS
```

## Notes

- The exported COMSOL text header may show garbled Chinese descriptions on some Windows setups. Numeric columns are unaffected.
- If the script reports `Failed to connect to server`, check whether port `2036` is occupied or whether `comsolmphserver.exe` can start normally.
- This demo intentionally keeps the geometry simple so that material domains and electrode domains are easy to inspect.
