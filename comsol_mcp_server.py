"""
COMSOL 6.4 MCP Server - Python + COMSOL java.exe
Full automation: geometry, physics, mesh, study, eval, magnetization.
"""

import os, subprocess, tempfile

COMSOL_MPH = r"D:\Program Files\COMSOL\COMSOL64\Multiphysics"
JAVA_EXE = os.path.join(COMSOL_MPH, "java", "win64", "jre", "bin", "java.exe")
LICENSE = r"D:\COMSOL 6.4\COMSOL 6.4\Crack\LMCOMSOL_Multiphysics_6.4_SSQ.lic"
TEMP_MODEL = os.path.join(os.environ.get("TEMP", tempfile.gettempdir()), "comsol_model.mph")
JAVA_TEMP = os.path.join(tempfile.gettempdir(), "ComsolRunner.java")

NATIVE_LIB = os.path.join(COMSOL_MPH, "lib", "win64") + ";" + os.path.join(COMSOL_MPH, "bin", "win64")
CLASSPATH = os.path.join(COMSOL_MPH, "plugins", "*") + ";" + os.path.join(COMSOL_MPH, "apiplugins", "*")

PHYSICS = {
    "mf": "InductionCurrents", "mfnc": "MagnetostaticsNoCurrents",
    "mef": "ElectricInductionCurrents", "es": "Electrostatics",
    "ec": "ConductiveMedia", "ht": "HeatTransferInSolidsAndFluids",
    "solid": "SolidMechanics",
}

JAVA_HEADER = "import com.comsol.model.*;\nimport com.comsol.model.util.*;"
LOAD = f'ModelUtil.initStandalone(false); Model m; try{{m=ModelUtil.load("{TEMP_MODEL.replace(chr(92),chr(92)+chr(92))}");}}catch(Exception e){{m=ModelUtil.create("Model");}}'
SAVE = f'm.save("{TEMP_MODEL.replace(chr(92),chr(92)+chr(92))}");'


def _run(code: str, timeout: int = 300) -> str:
    with open(JAVA_TEMP, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    env = os.environ.copy()
    env["COMSOL_LICENSE_FILE"] = LICENSE
    env["LMCOMSOL_LICENSE_FILE"] = LICENSE
    try:
        r = subprocess.run([JAVA_EXE, "-cp", CLASSPATH,
            f"-Djava.library.path={NATIVE_LIB}", f"-Dcs.root={COMSOL_MPH}", JAVA_TEMP],
            capture_output=True, text=True, timeout=timeout, env=env)
        out = r.stdout.strip()
        if r.returncode != 0:
            err = r.stderr.strip()
            if err: out += "\n" + err
        return out if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception as e:
        return f"Error: {e}"


from fastmcp import FastMCP
mcp = FastMCP("COMSOL 6.4")


@mcp.tool()
def comsol_new(name: str = "Model") -> str:
    """Create new empty model."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{ModelUtil.initStandalone(false);Model m=ModelUtil.create("{name}");m.save("{TEMP_MODEL.replace(chr(92),chr(92)+chr(92))}");System.out.println("OK: "+m.name());}}}}')


@mcp.tool()
def comsol_open(filepath: str) -> str:
    """Load .mph file."""
    p = filepath.replace("\\", "\\\\")
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{ModelUtil.initStandalone(false);Model m=ModelUtil.load("{p}");m.save("{TEMP_MODEL.replace(chr(92),chr(92)+chr(92))}");System.out.println("OK: "+m.name());}}}}')


@mcp.tool()
def comsol_save(filepath: str) -> str:
    """Save model to .mph file."""
    p = filepath.replace("\\", "\\\\")
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};m.save("{p}");System.out.println("OK: saved");}}}}')


@mcp.tool()
def comsol_info() -> str:
    """Get model info: name, components, physics."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};System.out.println("name: "+m.name());for(String k:m.component().keys())System.out.println("component: "+k);{SAVE}}}}}')


@mcp.tool()
def comsol_block(comp: str = "comp1", w: float = 1.0, h: float = 1.0, d: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> str:
    """Create 3D block."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};ModelNode c=m.component().create("{comp}",true);GeomSequence g=c.geom().create("geom1",3);g.create("blk1","Block");g.feature("blk1").set("size",new double[]{{{w},{h},{d}}});g.feature("blk1").set("pos",new double[]{{{x},{y},{z}}});g.run();System.out.println("OK: block {w}x{h}x{d}");{SAVE}}}}}')


@mcp.tool()
def comsol_cylinder(comp: str = "comp1", r: float = 0.1, h: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> str:
    """Create 3D cylinder."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};ModelNode c=m.component().create("{comp}",true);GeomSequence g=c.geom().create("geom1",3);g.create("cyl1","Cylinder");g.feature("cyl1").set("r",{r});g.feature("cyl1").set("h",{h});g.feature("cyl1").set("pos",new double[]{{{x},{y},{z}}});g.run();System.out.println("OK: cylinder r={r} h={h}");{SAVE}}}}}')


@mcp.tool()
def comsol_sphere(comp: str = "comp1", r: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> str:
    """Create 3D sphere."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};ModelNode c=m.component().create("{comp}",true);GeomSequence g=c.geom().create("geom1",3);g.create("sph1","Sphere");g.feature("sph1").set("r",{r});g.feature("sph1").set("pos",new double[]{{{x},{y},{z}}});g.run();System.out.println("OK: sphere r={r}");{SAVE}}}}}')




@mcp.tool()
def comsol_airbox(comp: str = "comp1", w: float = 0.04, h: float = 0.02, d: float = 0.008,
                  x: float = -0.015, y: float = -0.0075, z: float = -0.003) -> str:
    """Create air domain block surrounding the magnet. Default surrounds a 10x5x2mm magnet."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};ModelNode c=m.component("{comp}");GeomSequence g=c.geom("geom1");g.create("blk2","Block");g.feature("blk2").set("size",new double[]{{{w},{h},{d}}});g.feature("blk2").set("pos",new double[]{{{x},{y},{z}}});g.run();System.out.println("OK: air box {w}x{h}x{d}");{SAVE}}}}}')


@mcp.tool()
def comsol_material(comp: str = "comp1", domain: int = 2, material: str = "Air") -> str:
    """Set material on a domain. material: Air, Copper, Iron, etc."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};m.component("{comp}").material().create("mat{domain}","Common");m.component("{comp}").material("mat{domain}").set("family","{material.lower()}");m.component("{comp}").material("mat{domain}").selection().set({domain});System.out.println("OK: material {material} on domain {domain}");{SAVE}}}}}')@mcp.tool()
def comsol_mesh(comp: str = "comp1", size: str = "normal") -> str:
    """Mesh. size: finer, fine, normal, coarse, coarser."""
    sz = {"finer": 3, "fine": 4, "normal": 5, "coarse": 6, "coarser": 7}.get(size.lower(), 5)
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};MeshSequence mesh=m.component("{comp}").mesh().create("mesh1","geom1");mesh.autoMeshSize({sz});mesh.run();System.out.println("OK: meshed size={size}");{SAVE}}}}}')


@mcp.tool()
def comsol_physics(comp: str = "comp1", phys: str = "mf") -> str:
    """Add physics. Options: mf, mfnc, mef, es, ec, ht, solid."""
    pid = PHYSICS.get(phys.lower(), phys)
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};m.component("{comp}").physics().create("{phys}","{pid}","geom1");System.out.println("OK: physics {phys} ({pid})");{SAVE}}}}}')


@mcp.tool()
def comsol_magnetize(comp: str = "comp1", phys_tag: str = "mf", br_x: float = 0.0, br_y: float = 0.0, br_z: float = 1.44) -> str:
    """Set permanent magnet remanent flux density (Br) in [T]. Use after comsol_physics with mf or mfnc."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};com.comsol.model.physics.Physics phys=m.component("{comp}").physics("{phys_tag}");phys.create("mfcs1","MagneticFluxConservationSolid",3);com.comsol.model.physics.PhysicsFeature f=phys.feature("mfcs1");f.selection().set(1);f.set("ConstitutiveRelationBH","RemanentFluxDensity");f.set("mur_crel_BH_RemanentFluxDensity_mat","userdef");f.set("mur_crel_BH_RemanentFluxDensity",new double[]{1.05,0,0,0,1.05,0,0,0,1.05});f.set("normBr_crel_BH_RemanentFluxDensity_mat","userdef");f.set("normBr_crel_BH_RemanentFluxDensity",{br_z});f.set("e_crel_BH_RemanentFluxDensity",new int[]{0,0,0});f.set("e_crel_BH_RemanentFluxDensity",new int[]{{(int){br_x},(int){br_y},(int){br_z}}});System.out.println("OK: Br=({br_x},{br_y},{br_z})T");{SAVE}}}}}')


@mcp.tool()
def comsol_study(study_type: str = "stationary") -> str:
    """Create+run study. type: stationary, frequency, time, eigenfrequency."""
    t = {"stationary": "std", "frequency": "freq", "time": "tran", "eigenfrequency": "eig"}.get(study_type.lower(), "std")
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};m.study().create("{t}1");m.study("{t}1").run();System.out.println("OK: study {study_type} done");{SAVE}}}}}')


@mcp.tool()
def comsol_solve() -> str:
    """Run all solver steps."""
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};m.sol().runAll();System.out.println("OK: solved");{SAVE}}}}}')


@mcp.tool()
def comsol_eval(expr: str) -> str:
    """Evaluate expression, return value."""
    s = expr.replace("\\", "\\\\").replace('"', '\\"')
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};NumericalFeature ev=m.result().numerical().create("ev1","Eval");ev.set("expr","{s}");try{{double[][]v=ev.getReal();System.out.println(v!=null&&v.length>0&&v[0].length>0?"RESULT:"+v[0][0]:"RESULT:no data");}}catch(Exception e){{System.out.println("ERROR:"+e.getMessage());}}{SAVE}}}}}')


@mcp.tool()
def comsol_global(expr: str) -> str:
    """Evaluate global matrix expression."""
    s = expr.replace("\\", "\\\\").replace('"', '\\"')
    return _run(f'{JAVA_HEADER}\nclass R{{public static void main(String[]a)throws Exception{{{LOAD};NumericalFeature gv=m.result().numerical().create("gv1","Global");gv.set("expr","{s}");try{{double[][]v=gv.getReal();System.out.println(v!=null&&v.length>0&&v[0].length>0?"RESULT:"+v[0][0]:"RESULT:no data");}}catch(Exception e){{System.out.println("ERROR:"+e.getMessage());}}{SAVE}}}}}')


def main():
    mcp.run()

if __name__ == "__main__":
    main()


