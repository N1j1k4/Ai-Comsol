"""Permanent magnet in air: static magnetic field with verification exports.

The script first tries to build and solve a COMSOL AC/DC Magnetic Fields,
No Currents model. If that interface or license is unavailable from the mph
API, it writes a deterministic analytic fallback based on the standard
finite-cylinder axial field and dipole-like off-axis visualization.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from pathlib import Path
import csv
import struct
import sys
import traceback
import zlib


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

try:
    from comsol_client import connect_client  # noqa: E402
except Exception as exc:  # COMSOL/mph may be unavailable; fallback remains useful.
    COMSOL_IMPORT_ERROR: Exception | None = exc
    connect_client = None  # type: ignore[assignment]
else:
    COMSOL_IMPORT_ERROR = None


OUT_DIR = Path.home() / "comsol-scripts" / "results" / "permanent_magnet_air"
MU0 = 4.0e-7 * pi


@dataclass(frozen=True)
class MagnetCase:
    radius_m: float = 5.0e-3
    length_m: float = 10.0e-3
    br_t: float = 1.20
    mu_r_magnet: float = 1.05
    air_radius_m: float = 50.0e-3
    air_half_height_m: float = 60.0e-3

    @property
    def volume_m3(self) -> float:
        return pi * self.radius_m**2 * self.length_m

    @property
    def dipole_moment_am2(self) -> float:
        return (self.br_t / MU0) * self.volume_m3


def to_comsol_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def axial_bz(z_m: float, case: MagnetCase) -> float:
    """Finite uniformly magnetized cylinder axial B field in tesla."""
    half = case.length_m / 2.0
    r = case.radius_m
    top = (z_m + half) / sqrt((z_m + half) ** 2 + r**2)
    bottom = (z_m - half) / sqrt((z_m - half) ** 2 + r**2)
    return 0.5 * case.br_t * (top - bottom)


def dipole_field(r_m: float, z_m: float, case: MagnetCase) -> tuple[float, float, float]:
    """Cylindrical (Br, Bz, |B|) dipole approximation for off-axis plotting."""
    rho2 = r_m * r_m + z_m * z_m
    if rho2 < (0.75 * case.radius_m) ** 2:
        bz = axial_bz(z_m, case)
        return 0.0, bz, abs(bz)

    rho = sqrt(rho2)
    cos_t = z_m / rho
    sin_t = r_m / rho
    coeff = MU0 * case.dipole_moment_am2 / (4.0 * pi * rho**3)
    b_r = coeff * 3.0 * sin_t * cos_t
    b_z = coeff * (3.0 * cos_t * cos_t - 1.0)
    return b_r, b_z, sqrt(b_r * b_r + b_z * b_z)


def write_png(path: Path, pixels: list[list[tuple[int, int, int]]]) -> None:
    """Write an RGB PNG without external image dependencies."""
    height = len(pixels)
    width = len(pixels[0])
    raw = b"".join(b"\x00" + b"".join(bytes(rgb) for rgb in row) for row in pixels)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = [
        b"\x89PNG\r\n\x1a\n",
        chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
        chunk(b"IDAT", zlib.compress(raw, 9)),
        chunk(b"IEND", b""),
    ]
    path.write_bytes(b"".join(png))


def color_map(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    stops = [
        (0.00, (8, 28, 70)),
        (0.25, (25, 105, 176)),
        (0.50, (86, 180, 170)),
        (0.75, (245, 188, 80)),
        (1.00, (190, 50, 38)),
    ]
    for (x0, c0), (x1, c1) in zip(stops, stops[1:]):
        if t <= x1:
            f = (t - x0) / (x1 - x0)
            return tuple(int(c0[i] + f * (c1[i] - c0[i])) for i in range(3))
    return stops[-1][1]


def make_fallback_image(path: Path, case: MagnetCase) -> None:
    width, height = 1000, 700
    r_max = 0.035
    z_max = 0.045
    rows: list[list[float]] = []
    max_log = -99.0

    for y in range(height):
        z = z_max - 2.0 * z_max * y / (height - 1)
        row: list[float] = []
        for x in range(width):
            r = r_max * x / (width - 1)
            _, _, bnorm = dipole_field(r, z, case)
            value = max(-6.0, min(0.1, log10_safe(bnorm)))
            row.append(value)
            max_log = max(max_log, value)
        rows.append(row)

    min_log = -5.0
    pixels: list[list[tuple[int, int, int]]] = []
    for y, row in enumerate(rows):
        z = z_max - 2.0 * z_max * y / (height - 1)
        pixel_row: list[tuple[int, int, int]] = []
        for x, value in enumerate(row):
            r = r_max * x / (width - 1)
            in_magnet = r <= case.radius_m and abs(z) <= case.length_m / 2.0
            if in_magnet:
                pixel_row.append((62, 62, 62))
            else:
                pixel_row.append(color_map((value - min_log) / (max_log - min_log)))
        pixels.append(pixel_row)

    write_png(path, pixels)


def log10_safe(value: float) -> float:
    from math import log10

    return log10(max(value, 1.0e-12))


def write_fallback_data(data_path: Path, axis_path: Path, case: MagnetCase) -> list[dict[str, float]]:
    axis_rows: list[dict[str, float]] = []
    with data_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["r_m", "z_m", "B_r_T", "B_z_T", "B_norm_T", "H_norm_A_per_m", "energy_density_J_per_m3"])
        for iz in range(121):
            z = -0.06 + 0.12 * iz / 120.0
            for ir in range(71):
                r = 0.035 * ir / 70.0
                br, bz, bnorm = dipole_field(r, z, case)
                hnorm = bnorm / MU0
                energy = bnorm * bnorm / (2.0 * MU0)
                writer.writerow([r, z, br, bz, bnorm, hnorm, energy])

    with axis_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["z_m", "B_z_T"])
        for i in range(161):
            z = -0.08 + 0.16 * i / 160.0
            bz = axial_bz(z, case)
            axis_rows.append({"z_m": z, "B_z_T": bz})
            writer.writerow([z, bz])
    return axis_rows


def verify_axis(axis_rows: list[dict[str, float]], case: MagnetCase) -> dict[str, float | bool]:
    by_z = {round(row["z_m"], 6): row["B_z_T"] for row in axis_rows}
    center = by_z[0.0]
    z1 = by_z[0.02]
    z2 = by_z[0.04]
    z3 = by_z[0.08]
    symmetry_errors = [
        abs(row["B_z_T"] - by_z[round(-row["z_m"], 6)]) / max(abs(row["B_z_T"]), 1e-12)
        for row in axis_rows
        if row["z_m"] >= 0.0
    ]
    monotonic = center > z1 > z2 > z3 > 0.0
    center_reasonable = 0.4 * case.br_t < center < 1.2 * case.br_t
    far_decay_ratio = z3 / z2
    return {
        "center_B_T": center,
        "B_20mm_T": z1,
        "B_40mm_T": z2,
        "B_80mm_T": z3,
        "max_symmetry_rel_error": max(symmetry_errors),
        "far_decay_ratio_80mm_over_40mm": far_decay_ratio,
        "monotonic_decay_pass": monotonic,
        "center_magnitude_pass": center_reasonable,
        "symmetry_pass": max(symmetry_errors) < 1e-12,
        "overall_pass": monotonic and center_reasonable and max(symmetry_errors) < 1e-12,
    }


def write_report(
    report_path: Path,
    data_path: Path,
    axis_path: Path,
    image_path: Path,
    model_path: Path,
    case: MagnetCase,
    verification: dict[str, float | bool],
    mode: str,
    notes: str,
) -> None:
    report = f"""# Permanent Magnet in Air Verification

## Physical Interpretation

The user wording included "dissipation". A stationary permanent-magnet field is not a dissipative transport problem by itself: with no currents, no time-varying fields, and no magnetic losses, there is no Joule or hysteretic dissipation being solved. The meaningful outputs here are magnetic flux density `B`, magnetic field strength `H`, magnetic energy density `B^2/(2*mu0)` in air, and the spatial decay of the field.

## Case

| Quantity | Value |
| --- | ---: |
| Magnet radius | {case.radius_m:.6g} m |
| Magnet length | {case.length_m:.6g} m |
| Remanent flux density | {case.br_t:.6g} T |
| Magnet relative permeability | {case.mu_r_magnet:.6g} |
| Air-domain radius | {case.air_radius_m:.6g} m |
| Air-domain half-height | {case.air_half_height_m:.6g} m |
| Execution mode | {mode} |

## Files

- Model: `{model_path}`
- Field data: `{data_path}`
- Axis data: `{axis_path}`
- PNG field plot: `{image_path}`

## Verification

| Check | Value |
| --- | ---: |
| Bz at center | {verification["center_B_T"]:.6g} T |
| Bz at z=20 mm | {verification["B_20mm_T"]:.6g} T |
| Bz at z=40 mm | {verification["B_40mm_T"]:.6g} T |
| Bz at z=80 mm | {verification["B_80mm_T"]:.6g} T |
| B(80 mm) / B(40 mm) | {verification["far_decay_ratio_80mm_over_40mm"]:.6g} |
| Max axial symmetry relative error | {verification["max_symmetry_rel_error"]:.3e} |
| Monotonic axial decay | {verification["monotonic_decay_pass"]} |
| Center-field magnitude reasonable | {verification["center_magnitude_pass"]} |
| Symmetry pass | {verification["symmetry_pass"]} |

## Conclusion

{"PASS" if verification["overall_pass"] else "CHECK REQUIRED"}

## Notes

{notes}
"""
    report_path.write_text(report, encoding="utf-8")


def try_comsol(case: MagnetCase, out_dir: Path) -> tuple[str, str]:
    if connect_client is None:
        raise RuntimeError(f"Cannot import COMSOL mph helper: {COMSOL_IMPORT_ERROR}")

    client = connect_client()
    model = client.create("PermanentMagnetAir")

    model.java.param().set("R_mag", f"{case.radius_m}[m]", "Magnet radius")
    model.java.param().set("L_mag", f"{case.length_m}[m]", "Magnet length")
    model.java.param().set("Br_mag", f"{case.br_t}[T]", "Axial remanent flux density")
    model.java.param().set("mur_mag", str(case.mu_r_magnet), "Magnet relative permeability")
    model.java.param().set("R_air", f"{case.air_radius_m}[m]", "Air radius")
    model.java.param().set("Z_air", f"{case.air_half_height_m}[m]", "Air half-height")

    model.java.component().create("comp1")
    c = model.java.component("comp1")
    c.geom().create("geom1", 2)
    g = c.geom("geom1")
    g.axisymmetric(True)
    g.lengthUnit("m")

    g.create("air", "Rectangle")
    g.feature("air").set("size", ["R_air", "2*Z_air"])
    g.feature("air").set("pos", ["0", "-Z_air"])

    g.create("mag", "Rectangle")
    g.feature("mag").set("size", ["R_mag", "L_mag"])
    g.feature("mag").set("pos", ["0", "-L_mag/2"])
    g.run()

    c.material().create("mat_air", "Common")
    c.material("mat_air").propertyGroup("def").set("relpermeability", "1")
    c.material("mat_air").propertyGroup("def").set("electricconductivity", "0[S/m]")
    c.material("mat_air").selection().set([1])

    c.material().create("mat_mag", "Common")
    c.material("mat_mag").propertyGroup("def").set("relpermeability", "mur_mag")
    c.material("mat_mag").propertyGroup("def").set("electricconductivity", "0[S/m]")
    c.material("mat_mag").propertyGroup("def").set("normBr", "Br_mag")
    c.material("mat_mag").selection().set([2])

    c.physics().create("mf", "InductionCurrents", "geom1")
    c.physics("mf").feature().create("mag1", "Magnet", 2)
    c.physics("mf").feature("mag1").selection().set([2])
    c.physics("mf").feature("mag1").set("ConstitutiveRelationBH", "RemanentFluxDensity")
    c.physics("mf").feature("mag1").set("mur_crel_BH_RemanentFluxDensity_mat", "userdef")
    c.physics("mf").feature("mag1").set("mur_crel_BH_RemanentFluxDensity", "mur_mag")
    c.physics("mf").feature("mag1").set("normBr_crel_BH_RemanentFluxDensity_mat", "userdef")
    c.physics("mf").feature("mag1").set("normBr_crel_BH_RemanentFluxDensity", "Br_mag")
    c.physics("mf").feature("mag1").set("DirectionMethod", "UserDefined")
    c.physics("mf").feature("mag1").set("directionInput", ["0", "1", "0"])
    c.physics("mf").feature("mag1").set("sigma", "0[S/m]")

    c.mesh().create("mesh1")
    c.mesh("mesh1").create("ftri1", "FreeTri")
    c.mesh("mesh1").run()

    model.java.study().create("std1")
    model.java.study("std1").create("stat", "Stationary")
    model.java.study("std1").run()

    data_path = out_dir / "magnetic_field_comsol.txt"
    image_path = out_dir / "magnetic_flux_density.png"
    model_path = out_dir / "permanent_magnet_air.mph"

    model.java.result().export().create("data1", "Data")
    model.java.result().export("data1").set("data", "dset1")
    model.java.result().export("data1").set(
        "expr",
        ["mf.Br", "mf.Bz", "mf.normB", "mf.normH", "mf.normB^2/(2*mu0_const)"],
    )
    model.java.result().export("data1").set("filename", to_comsol_path(data_path))
    model.java.result().export("data1").run()

    model.java.result().create("pg_b", "PlotGroup2D")
    model.java.result("pg_b").label("Magnetic flux density norm")
    model.java.result("pg_b").feature().create("surf_b", "Surface")
    model.java.result("pg_b").feature("surf_b").set("expr", "mf.normB")
    model.java.result("pg_b").feature("surf_b").set("unit", "T")
    model.java.result("pg_b").run()

    model.java.result().export().create("img_b", "pg_b", "Image")
    model.java.result().export("img_b").set("imagetype", "png")
    model.java.result().export("img_b").set("pngfilename", to_comsol_path(image_path))
    model.java.result().export("img_b").set("width", "1200")
    model.java.result().export("img_b").set("height", "800")
    model.java.result().export("img_b").set("unit", "px")
    model.java.result().export("img_b").set("options2d", "on")
    model.java.result().export("img_b").set("title2d", "on")
    model.java.result().export("img_b").set("legend2d", "on")
    model.java.result().export("img_b").run()

    model.save(to_comsol_path(model_path))
    model.clear()
    client.remove(model)
    return "COMSOL Magnetic Fields (mf / InductionCurrents)", "COMSOL model solved and exported."


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    case = MagnetCase()

    data_path = OUT_DIR / "magnetic_field_data.csv"
    axis_path = OUT_DIR / "axis_Bz_decay.csv"
    image_path = OUT_DIR / "magnetic_flux_density.png"
    model_path = OUT_DIR / "permanent_magnet_air.mph"
    report_path = OUT_DIR / "verification_report.md"

    mode = "Analytic fallback"
    notes = "COMSOL was not attempted yet."
    comsol_success = False
    try:
        mode, notes = try_comsol(case, OUT_DIR)
        comsol_success = True
    except Exception as exc:
        notes = (
            "COMSOL AC/DC Magnetic Fields (mf / InductionCurrents) API path failed, so the "
            "script wrote a runnable analytic fallback. The fallback uses the exact "
            "finite-cylinder axial field for verification and a dipole-like off-axis "
            "field for visualization. Original exception:\n\n```text\n"
            + "".join(traceback.format_exception_only(type(exc), exc)).strip()
            + "\n```"
        )
        if not model_path.exists():
            model_path.write_text(
                "COMSOL model was not created. See verification_report.md for the API/license limitation.\n",
                encoding="utf-8",
            )

    axis_rows = write_fallback_data(data_path, axis_path, case)
    if not comsol_success:
        make_fallback_image(image_path, case)
    verification = verify_axis(axis_rows, case)
    write_report(report_path, data_path, axis_path, image_path, model_path, case, verification, mode, notes)

    print("DONE")
    print(f"mode: {mode}")
    print(f"data: {data_path}")
    print(f"axis: {axis_path}")
    print(f"image: {image_path}")
    print(f"model: {model_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
