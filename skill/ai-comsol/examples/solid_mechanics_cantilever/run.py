"""Demo: 3D solid-mechanics cantilever beam with end load verification."""
from __future__ import annotations

from pathlib import Path
import math
import sys


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from comsol_client import connect_client  # noqa: E402


OUT_DIR = Path.home() / "comsol-scripts" / "results" / "solid_mechanics_cantilever"


def to_comsol_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def read_displacement_data(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            try:
                values = [float(value) for value in parts[:7]]
                # COMSOL exports this demo in mm because the geometry unit is mm.
                # Convert x, y, z, displacement magnitude, u, v, w to SI meters.
                rows.append([value * 1.0e-3 for value in values])
            except ValueError:
                continue
    return rows


def write_verification_report(data_path: Path, report_path: Path) -> None:
    rows = read_displacement_data(data_path)
    if not rows:
        raise RuntimeError(f"No numeric rows found in {data_path}")

    # 3D export columns: x, y, z, solid.disp, u, v, w.
    disp_values = [row[3] for row in rows]
    w_values = [row[6] for row in rows]

    length_m = 0.10
    width_m = 0.010
    height_m = 0.005
    force_n = -10.0
    youngs_pa = 200e9
    moment_i_m4 = width_m * height_m**3 / 12.0
    theory_delta_m = abs(force_n) * length_m**3 / (3.0 * youngs_pa * moment_i_m4)

    # Use the average vertical displacement on the free-end face x ~= L.
    end_tol = length_m * 1.0e-4
    end_rows = [row for row in rows if abs(row[0] - length_m) <= end_tol]
    if not end_rows:
        max_x = max(row[0] for row in rows)
        end_tol = max(length_m * 1.0e-3, abs(max_x) * 1.0e-6)
        end_rows = [row for row in rows if abs(row[0] - max_x) <= end_tol]

    if not end_rows:
        raise RuntimeError("No rows found on the free-end face for verification.")

    end_w_avg_m = sum(row[6] for row in end_rows) / len(end_rows)
    end_w_abs_m = abs(end_w_avg_m)
    rel_error = abs(end_w_abs_m - theory_delta_m) / theory_delta_m

    max_disp = max(disp_values)
    max_row = max(rows, key=lambda row: row[3])
    passed = rel_error < 0.20 and end_w_avg_m < 0.0

    report = f"""# Solid Mechanics Cantilever Verification

## Files

- Data: `{data_path}`
- Report: `{report_path}`

## Geometry, Material, and Load

| Quantity | Value |
| --- | ---: |
| Beam length L | {length_m:.6g} m |
| Beam width b | {width_m:.6g} m |
| Beam height h | {height_m:.6g} m |
| Young's modulus E | {youngs_pa:.6g} Pa |
| Poisson's ratio nu | 0.30 |
| Free-end force Fz | {force_n:.6g} N |

The rectangular cross-section bends about the y axis under a z-direction end load, so:

```text
I = b*h^3/12 = {moment_i_m4:.6g} m^4
delta = F*L^3/(3*E*I) = {theory_delta_m:.6g} m
```

## Result Summary

| Quantity | Value |
| --- | ---: |
| Data rows | {len(rows)} |
| Free-end rows | {len(end_rows)} |
| Free-end average w | {end_w_avg_m:.6g} m |
| Free-end average |w| | {end_w_abs_m:.6g} m |
| Beam-theory delta | {theory_delta_m:.6g} m |
| Relative error | {rel_error:.3%} |
| Global max displacement magnitude | {max_disp:.6g} m |
| Max displacement location | x={max_row[0]:.6g} m, y={max_row[1]:.6g} m, z={max_row[2]:.6g} m |

## Conclusion

{"PASS" if passed else "CHECK REQUIRED"}

The COMSOL model uses a 3D solid continuum, while the check uses Euler-Bernoulli beam theory.
A tolerance of 20% is used for this coarse automatic demo mesh.
"""
    report_path.write_text(report, encoding="utf-8")


def try_set(feature, key: str, value) -> str | None:
    try:
        feature.set(key, value)
        return None
    except Exception as exc:  # COMSOL image/export properties vary by version.
        return f"{key}={value!r}: {exc}"


def export_image(model, plot_tag: str, export_tag: str, image_path: Path) -> list[str]:
    notes: list[str] = []
    exp = model.java.result().export()
    exp.create(export_tag, plot_tag, "Image")
    image_export = model.java.result().export(export_tag)
    for key, value in [
        ("imagetype", "png"),
        ("pngfilename", to_comsol_path(image_path)),
        ("width", "1400"),
        ("height", "900"),
        ("unit", "px"),
        ("legend3d", "on"),
        ("title3d", "on"),
    ]:
        note = try_set(image_export, key, value)
        if note:
            notes.append(note)
    image_export.run()
    return notes


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    client = connect_client()
    model = client.create("SolidMechanicsCantilever")

    model.java.param().set("beam_L", "100[mm]", "Beam length")
    model.java.param().set("beam_b", "10[mm]", "Beam width in y")
    model.java.param().set("beam_h", "5[mm]", "Beam height in z")
    model.java.param().set("Fz", "-10[N]", "Total downward force at free end")
    model.java.param().set("E_beam", "200[GPa]", "Young's modulus")
    model.java.param().set("nu_beam", "0.30", "Poisson's ratio")
    model.java.param().set("rho_beam", "7850[kg/m^3]", "Density")

    model.java.component().create("comp1")
    c = model.java.component("comp1")
    c.geom().create("geom1", 3)
    g = c.geom("geom1")
    g.lengthUnit("mm")

    g.create("beam", "Block")
    g.feature("beam").set("size", ["beam_L", "beam_b", "beam_h"])
    g.feature("beam").set("pos", ["0", "-beam_b/2", "-beam_h/2"])
    g.run()

    c.material().create("mat_steel", "Common")
    c.material("mat_steel").propertyGroup("def").set("youngsmodulus", "E_beam")
    c.material("mat_steel").propertyGroup("def").set("poissonsratio", "nu_beam")
    c.material("mat_steel").propertyGroup("def").set("density", "rho_beam")
    c.material("mat_steel").selection().set([1])

    c.physics().create("solid", "SolidMechanics", "geom1")

    # Boundary numbering for the axis-aligned block is expected to include x=0 and x=L faces.
    # If a local COMSOL version assigns boundaries differently, inspect the saved MPH and adjust
    # fixed_boundary/free_end_boundary below.
    fixed_boundary = 1
    free_end_boundary = 6

    c.physics("solid").feature().create("fix1", "Fixed", 2)
    c.physics("solid").feature("fix1").selection().set([fixed_boundary])

    c.physics("solid").feature().create("bndl1", "BoundaryLoad", 2)
    c.physics("solid").feature("bndl1").selection().set([free_end_boundary])
    c.physics("solid").feature("bndl1").set("LoadType", "TotalForce")
    c.physics("solid").feature("bndl1").set("Ftot", ["0", "0", "Fz"])

    c.mesh().create("mesh1")
    c.mesh("mesh1").create("ftet1", "FreeTet")
    c.mesh("mesh1").feature("size").set("hauto", "4")
    c.mesh("mesh1").run()

    model.java.study().create("std1")
    model.java.study("std1").create("stat", "Stationary")
    model.java.study("std1").run()

    data_path = OUT_DIR / "displacement_data.txt"
    deformed_image_path = OUT_DIR / "deformed_shape.png"
    displacement_image_path = OUT_DIR / "displacement_magnitude.png"
    model_path = OUT_DIR / "solid_mechanics_cantilever.mph"
    report_path = OUT_DIR / "verification_report.md"
    notes_path = OUT_DIR / "export_notes.txt"

    model.java.result().export().create("data1", "Data")
    model.java.result().export("data1").set("data", "dset1")
    model.java.result().export("data1").set("expr", ["solid.disp", "u", "v", "w"])
    model.java.result().export("data1").set("filename", to_comsol_path(data_path))
    model.java.result().export("data1").run()

    model.java.result().create("pg_disp", "PlotGroup3D")
    model.java.result("pg_disp").label("Displacement magnitude")
    model.java.result("pg_disp").feature().create("surf_disp", "Surface")
    model.java.result("pg_disp").feature("surf_disp").set("expr", "solid.disp")
    model.java.result("pg_disp").feature("surf_disp").set("unit", "m")
    model.java.result("pg_disp").run()

    model.java.result().create("pg_def", "PlotGroup3D")
    model.java.result("pg_def").label("Deformed shape")
    model.java.result("pg_def").feature().create("surf_def", "Surface")
    model.java.result("pg_def").feature("surf_def").set("expr", "solid.disp")
    model.java.result("pg_def").feature("surf_def").set("unit", "m")
    model.java.result("pg_def").feature("surf_def").create("def1", "Deform")
    model.java.result("pg_def").feature("surf_def").feature("def1").set("scale", "100")
    model.java.result("pg_def").run()

    export_notes = []
    export_notes += export_image(model, "pg_disp", "img_disp", displacement_image_path)
    export_notes += export_image(model, "pg_def", "img_def", deformed_image_path)

    if export_notes:
        notes_path.write_text("\n".join(export_notes), encoding="utf-8")
    else:
        notes_path.write_text("No plot/export property fallbacks were needed.\n", encoding="utf-8")

    model.save(to_comsol_path(model_path))
    write_verification_report(data_path, report_path)

    model.clear()
    client.remove(model)

    print("DONE")
    print(f"data: {data_path}")
    print(f"deformed image: {deformed_image_path}")
    print(f"displacement image: {displacement_image_path}")
    print(f"model: {model_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
