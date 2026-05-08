"""Simplified COMSOL demo: transient steel-plate impact deformation.

This case is intentionally a material-response visualization, not a
high-fidelity ballistic penetration or perforation predictor. It uses a
2D plane-strain steel plate with an equivalent half-sine pressure pulse over
the impact patch. The script exports the COMSOL model, time-history data,
verification notes, and tries to export PNG frames for animation.
"""
from __future__ import annotations

from pathlib import Path
import math
import sys


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from comsol_client import connect_client  # noqa: E402


OUT_DIR = Path.home() / "comsol-scripts" / "results" / "plate_projectile_impact"


def to_comsol_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def read_numeric_rows(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            try:
                rows.append([float(value) for value in parts])
            except ValueError:
                continue
    return rows


def write_verification_report(report_path: Path, data_path: Path, frame_dir: Path) -> None:
    rows = read_numeric_rows(data_path)
    max_umag = None
    fixed_umag = None
    peak_time = None
    passed = False

    if rows:
        # COMSOL exports this transient result as:
        # x, y, disp@t0, mises@t0, disp@t1, mises@t1, ...
        disp_columns = list(range(2, len(rows[0]), 2))
        disp_values = [
            row[column]
            for row in rows
            for column in disp_columns
            if len(row) > column
        ]
        if disp_values and disp_columns:
            max_umag = max(disp_values)
            peak_column = max(
                disp_columns,
                key=lambda column: max(row[column] for row in rows if len(row) > column),
            )
            peak_time = ((peak_column - 2) // 2) * 1.0e-6

        fixed_candidates = [
            row[column]
            for row in rows
            for column in disp_columns
            if len(row) > column and abs(row[0] + 0.05) < 1e-6
        ]
        if fixed_candidates:
            fixed_umag = max(abs(value) for value in fixed_candidates)

        if max_umag is not None and fixed_umag is not None and peak_time is not None:
            passed = max_umag > 0 and fixed_umag < max_umag * 0.05 and peak_time >= 8.0e-6

    frame_count = len(list(frame_dir.glob("frame_*.png"))) if frame_dir.exists() else 0

    max_umag_text = "not available" if max_umag is None else f"{max_umag:.6e} m"
    fixed_text = "not available" if fixed_umag is None else f"{fixed_umag:.6e} m"
    peak_time_text = "not available" if peak_time is None else f"{peak_time:.6e} s"

    report = f"""# Plate Projectile Impact Verification Report

## Scope

This is a simplified transient solid-mechanics impact-deformation demo.
It does not model penetration, fracture, erosion, thermal softening, contact,
or projectile optimization. It visualizes the steel plate response to an
equivalent short pressure pulse.

## Files

- Model: `{OUT_DIR / "plate_projectile_impact.mph"}`
- Data: `{data_path}`
- PNG frames directory: `{frame_dir}`

## Verification Checks

| Check | Current value | Intended result |
| --- | ---: | --- |
| Maximum displacement magnitude | {max_umag_text} | Nonzero and peaks after the pressure pulse begins |
| Peak-displacement time | {peak_time_text} | Near or after the pulse duration, not before loading |
| Fixed left boundary displacement | {fixed_text} | Close to zero relative to peak displacement |
| PNG visualization frames | {frame_count} | At least one frame if image export succeeds |

## Order-of-Magnitude Rationale

The demo uses steel with `E = 210 GPa`, `nu = 0.30`, and
`rho = 7850 kg/m^3`. The pressure pulse is intentionally moderate for a
stable visual demo, with a half-sine time history over a small central impact
patch. A microsecond-scale pulse should produce small elastic displacements,
typically in the micrometer-to-submillimeter range depending on mesh, boundary
conditions, and pulse amplitude.

## Status

{"PASS" if passed else "CHECK REQUIRED"}

This is a simplified visualization model. It is useful for testing transient
solid-mechanics automation and animation export, but it is not a penetration,
fracture, erosion, contact, or ballistic-performance model.
"""
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame_dir = OUT_DIR / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)

    client = connect_client()
    model = client.create("PlateProjectileImpactDemo")

    model.java.param().set("plate_L", "100[mm]", "Plate length")
    model.java.param().set("plate_H", "20[mm]", "Plate thickness in 2D section")
    model.java.param().set("patch_w", "8[mm]", "Equivalent impact patch width")
    model.java.param().set("p0", "250[MPa]", "Peak equivalent pressure")
    model.java.param().set("tp", "8[us]", "Half-sine pulse duration")
    model.java.param().set(
        "p_pulse",
        "p0*sin(pi*t/tp)*(t<=tp)",
        "Equivalent half-sine impact pulse",
    )

    model.java.component().create("comp1")
    c = model.java.component("comp1")
    c.geom().create("geom1", 2)
    g = c.geom("geom1")
    g.lengthUnit("m")

    g.create("plate", "Rectangle")
    g.feature("plate").set("size", ["plate_L", "plate_H"])
    g.feature("plate").set("pos", ["-plate_L/2", "-plate_H"])
    g.run()

    c.material().create("mat_steel", "Common")
    c.material("mat_steel").label("Structural steel, linear elastic")
    c.material("mat_steel").propertyGroup("def").set("youngsmodulus", "210e9[Pa]")
    c.material("mat_steel").propertyGroup("def").set("poissonsratio", "0.30")
    c.material("mat_steel").propertyGroup("def").set("density", "7850[kg/m^3]")
    c.material("mat_steel").selection().set([1])

    c.physics().create("solid", "SolidMechanics", "geom1")
    solid = c.physics("solid")
    solid.prop("StructuralTransientBehavior").set("StructuralTransientBehavior", "IncludeInertia")

    # Plane strain is a conservative simplification for a thick out-of-plane plate strip.
    try:
        solid.prop("d").set("AnalysisType", "PlaneStrain")
    except Exception:
        pass

    # Boundary numbering for this simple rectangle in COMSOL 6.4 was verified
    # from exported displacements: 1 left, 3 top, 4 right.
    solid.feature().create("fix_left", "Fixed", 1)
    solid.feature("fix_left").selection().set([1])

    solid.feature().create("load_top", "BoundaryLoad", 1)
    solid.feature("load_top").selection().set([3])
    solid.feature("load_top").set("LoadType", "ForceArea")
    solid.feature("load_top").set("FperArea", ["0", "-p_pulse", "0"])

    c.mesh().create("mesh1")
    c.mesh("mesh1").create("ftri1", "FreeTri")
    c.mesh("mesh1").feature("size").set("hauto", "3")
    c.mesh("mesh1").run()

    model.java.study().create("std1")
    model.java.study("std1").create("time", "Transient")
    model.java.study("std1").feature("time").set("tlist", "range(0,1[us],40[us])")
    model.java.study("std1").run()

    data_path = OUT_DIR / "impact_data.txt"
    model_path = OUT_DIR / "plate_projectile_impact.mph"
    report_path = OUT_DIR / "verification_report.md"

    model.java.result().export().create("data1", "Data")
    model.java.result().export("data1").set("data", "dset1")
    model.java.result().export("data1").set("expr", ["solid.disp", "solid.mises"])
    model.java.result().export("data1").set("filename", to_comsol_path(data_path))
    model.java.result().export("data1").run()

    model.java.result().create("pg_disp", "PlotGroup2D")
    model.java.result("pg_disp").label("Displacement magnitude")
    model.java.result("pg_disp").feature().create("surf_disp", "Surface")
    model.java.result("pg_disp").feature("surf_disp").set("expr", "solid.disp")
    model.java.result("pg_disp").feature("surf_disp").set("unit", "m")
    model.java.result("pg_disp").run()

    model.java.result().create("pg_def", "PlotGroup2D")
    model.java.result("pg_def").label("Deformed displacement magnitude")
    model.java.result("pg_def").feature().create("surf_def", "Surface")
    model.java.result("pg_def").feature("surf_def").set("expr", "solid.disp")
    model.java.result("pg_def").feature("surf_def").set("unit", "m")
    model.java.result("pg_def").feature("surf_def").create("def1", "Deform")
    model.java.result("pg_def").feature("surf_def").feature("def1").set("scale", "50")
    model.java.result("pg_def").run()

    # COMSOL image export from a transient dataset can vary by version. Keep a
    # best-effort static export so the model still produces at least one visual.
    image_path = frame_dir / "frame_displacement.png"
    deformed_image_path = frame_dir / "frame_deformed_displacement.png"
    try:
        model.java.result().export().create("img_disp", "pg_disp", "Image")
        model.java.result().export("img_disp").set("imagetype", "png")
        model.java.result().export("img_disp").set("pngfilename", to_comsol_path(image_path))
        model.java.result().export("img_disp").set("width", "1200")
        model.java.result().export("img_disp").set("height", "800")
        model.java.result().export("img_disp").set("unit", "px")
        model.java.result().export("img_disp").set("options2d", "on")
        model.java.result().export("img_disp").set("title2d", "on")
        model.java.result().export("img_disp").set("legend2d", "on")
        model.java.result().export("img_disp").run()

        model.java.result().export().create("img_def", "pg_def", "Image")
        model.java.result().export("img_def").set("imagetype", "png")
        model.java.result().export("img_def").set("pngfilename", to_comsol_path(deformed_image_path))
        model.java.result().export("img_def").set("width", "1200")
        model.java.result().export("img_def").set("height", "800")
        model.java.result().export("img_def").set("unit", "px")
        model.java.result().export("img_def").set("options2d", "on")
        model.java.result().export("img_def").set("title2d", "on")
        model.java.result().export("img_def").set("legend2d", "on")
        model.java.result().export("img_def").run()
    except Exception as exc:
        (OUT_DIR / "animation_export_note.txt").write_text(
            "COMSOL PNG export failed. Use the saved .mph file to export frames "
            f"from plot group pg_disp, or create a GIF from generated frames. Error: {exc}\n",
            encoding="utf-8",
        )

    model.save(to_comsol_path(model_path))
    write_verification_report(report_path, data_path, frame_dir)

    model.clear()
    client.remove(model)

    print("DONE")
    print(f"model: {model_path}")
    print(f"data: {data_path}")
    print(f"frames: {frame_dir}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
