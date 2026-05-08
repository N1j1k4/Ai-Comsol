"""Demo: 2D parallel-plate electrostatics with verification and image export."""
from __future__ import annotations

from pathlib import Path
import sys


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from comsol_client import connect_client  # noqa: E402


OUT_DIR = Path.home() / "comsol-scripts" / "results" / "electrostatics_2d_parallel_plate"


def to_comsol_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def read_field_data(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                rows.append([float(value) for value in parts[:6]])
            except ValueError:
                continue
    return rows


def write_verification_report(data_path: Path, report_path: Path) -> None:
    rows = read_field_data(data_path)
    if not rows:
        raise RuntimeError(f"No numeric rows found in {data_path}")

    # 2D export columns: x, y, V, es.normE, es.Ex, es.Ey.
    v_values = [row[2] for row in rows]
    e_values = [row[3] for row in rows]

    center_rows = [
        row for row in rows
        if abs(row[0]) < 1.0 and abs(row[1]) < 0.25
    ]
    if not center_rows:
        raise RuntimeError("No rows found in the center-gap verification region.")

    center_e_values = [row[3] for row in center_rows]

    voltage_delta = 2000.0  # +1000 V to -1000 V.
    inner_gap_m = 0.009  # Electrodes occupy 0.1 cm thickness, so inner gap is 0.9 cm.
    theory_e = voltage_delta / inner_gap_m
    center_e_avg = sum(center_e_values) / len(center_e_values)
    rel_error = abs(center_e_avg - theory_e) / theory_e
    passed = rel_error < 0.05 and min(v_values) >= -1000.1 and max(v_values) <= 1000.1

    max_e = max(e_values)
    max_row = max(rows, key=lambda row: row[3])

    report = f"""# 2D Parallel-Plate Electrostatics Verification

## Files

- Data: `{data_path}`
- Report: `{report_path}`

## Result Summary

| Quantity | Value |
| --- | ---: |
| Data rows | {len(rows)} |
| V min | {min(v_values):.6g} V |
| V max | {max(v_values):.6g} V |
| Global E max | {max_e:.6g} V/m |
| Global E max location | x={max_row[0]:.6g} cm, y={max_row[1]:.6g} cm |
| Center-region E avg | {center_e_avg:.6g} V/m |
| Theory center E | {theory_e:.6g} V/m |
| Relative error | {rel_error:.3%} |

## Verification Logic

The global maximum electric field is expected near electrode edges and corners, so it is not used as the main parallel-plate verification metric.
The central gap is checked with `abs(x) < 1.0 cm` and `abs(y) < 0.25 cm`.

The electrode faces are separated by 0.9 cm, not the full `gap = 1 cm`, because each electrode has thickness `gap / 10`.
Therefore the theoretical center field is:

```text
E = DeltaV / inner_gap = 2000 V / 0.009 m = {theory_e:.6g} V/m
```

## Conclusion

{"PASS" if passed else "CHECK REQUIRED"}
"""
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    client = connect_client()
    model = client.create("ParallelPlate2D")

    model.java.param().set("V_app", "1000[V]", "Applied voltage")
    model.java.param().set("W_elec", "5[cm]", "Electrode width")
    model.java.param().set("gap", "1[cm]", "Nominal electrode gap")

    model.java.component().create("comp1")
    c = model.java.component("comp1")
    c.geom().create("geom1", 2)
    g = c.geom("geom1")
    g.lengthUnit("cm")

    g.create("air", "Rectangle")
    g.feature("air").set("size", ["W_elec*4", "gap*4"])
    g.feature("air").set("pos", ["-W_elec*2", "-gap*2"])

    g.create("elec_neg", "Rectangle")
    g.feature("elec_neg").set("size", ["W_elec", "gap/10"])
    g.feature("elec_neg").set("pos", ["-W_elec/2", "-gap/2 - gap/20"])

    g.create("elec_pos", "Rectangle")
    g.feature("elec_pos").set("size", ["W_elec", "gap/10"])
    g.feature("elec_pos").set("pos", ["-W_elec/2", "gap/2 - gap/20"])
    g.run()

    c.material().create("mat_air", "Common")
    c.material("mat_air").propertyGroup("def").set("relpermittivity", "1")
    c.material("mat_air").selection().set([1])

    c.material().create("mat_elec", "Common")
    c.material("mat_elec").propertyGroup("def").set("relpermittivity", "1")
    c.material("mat_elec").selection().set([2, 3])

    c.physics().create("es", "Electrostatics", "geom1")

    c.physics("es").feature().create("term_pos", "DomainTerminal", 2)
    c.physics("es").feature("term_pos").selection().set([3])
    c.physics("es").feature("term_pos").set("TerminalType", "Voltage")
    c.physics("es").feature("term_pos").set("V0", "V_app")

    c.physics("es").feature().create("term_neg", "DomainTerminal", 2)
    c.physics("es").feature("term_neg").selection().set([2])
    c.physics("es").feature("term_neg").set("TerminalType", "Voltage")
    c.physics("es").feature("term_neg").set("V0", "-V_app")

    c.mesh().create("mesh1")
    c.mesh("mesh1").create("ftri1", "FreeTri")
    c.mesh("mesh1").run()

    model.java.study().create("std1")
    model.java.study("std1").create("stat", "Stationary")
    model.java.study("std1").run()

    data_path = OUT_DIR / "field_data.txt"
    image_path = OUT_DIR / "electric_field.png"
    model_path = OUT_DIR / "parallel_plate_2d.mph"
    report_path = OUT_DIR / "verification_report.md"

    model.java.result().export().create("data1", "Data")
    model.java.result().export("data1").set("data", "dset1")
    model.java.result().export("data1").set("expr", ["V", "es.normE", "es.Ex", "es.Ey"])
    model.java.result().export("data1").set("filename", to_comsol_path(data_path))
    model.java.result().export("data1").run()

    model.java.result().create("pg_e", "PlotGroup2D")
    model.java.result("pg_e").label("Electric field norm")
    model.java.result("pg_e").feature().create("surf_e", "Surface")
    model.java.result("pg_e").feature("surf_e").set("expr", "es.normE")
    model.java.result("pg_e").feature("surf_e").set("unit", "V/m")
    model.java.result("pg_e").run()

    model.java.result().export().create("img_e", "pg_e", "Image")
    model.java.result().export("img_e").set("imagetype", "png")
    model.java.result().export("img_e").set("pngfilename", to_comsol_path(image_path))
    model.java.result().export("img_e").set("width", "1200")
    model.java.result().export("img_e").set("height", "800")
    model.java.result().export("img_e").set("unit", "px")
    model.java.result().export("img_e").set("options2d", "on")
    model.java.result().export("img_e").set("title2d", "on")
    model.java.result().export("img_e").set("legend2d", "on")
    model.java.result().export("img_e").run()

    model.save(to_comsol_path(model_path))
    write_verification_report(data_path, report_path)

    model.clear()
    client.remove(model)

    print("DONE")
    print(f"data: {data_path}")
    print(f"image: {image_path}")
    print(f"model: {model_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
