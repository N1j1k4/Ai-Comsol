"""模板：2D 平行板电极静电场"""
import mph

client = mph.Client(cores=1)
model = client.create("ParallelElectrodes")

# === 参数 ===
model.java.param().set("V_app", "1000[V]", "施加电压")
model.java.param().set("W_elec", "5[cm]", "电极宽度")
model.java.param().set("gap", "1[cm]", "电极间隙")

# === 几何 ===
model.java.component().create("comp1")
c = model.java.component("comp1")
c.geom().create("geom1", 2)
g = c.geom("geom1"); g.lengthUnit("cm")

# 空气域
g.create("air", "Rectangle")
g.feature("air").set("size", ["W_elec*4", "gap*4"])
g.feature("air").set("pos", ["-W_elec*2", "-gap*2"])

# 电极1
g.create("elec1", "Rectangle")
g.feature("elec1").set("size", ["W_elec", "gap/10"])
g.feature("elec1").set("pos", ["-W_elec/2", "-gap/2 - gap/20"])

# 电极2
g.create("elec2", "Rectangle")
g.feature("elec2").set("size", ["W_elec", "gap/10"])
g.feature("elec2").set("pos", ["-W_elec/2", "gap/2 - gap/20"])

g.run()

# === 材料 ===
c.material().create("mat_air", "Common")
c.material("mat_air").propertyGroup("def").set("relpermittivity", "1")
c.material("mat_air").selection().set([1])

c.material().create("mat_elec", "Common")
c.material("mat_elec").propertyGroup("def").set("relpermittivity", "1")
c.material("mat_elec").selection().set([2, 3])

# === 物理场 ===
c.physics().create("es", "Electrostatics", "geom1")

# 正电极（域终端，2D用dim=2）
c.physics("es").feature().create("term_pos", "DomainTerminal", 2)
c.physics("es").feature("term_pos").selection().set([3])
c.physics("es").feature("term_pos").set("TerminalType", "Voltage")
c.physics("es").feature("term_pos").set("V0", "V_app")

# 负电极
c.physics("es").feature().create("term_neg", "DomainTerminal", 2)
c.physics("es").feature("term_neg").selection().set([2])
c.physics("es").feature("term_neg").set("TerminalType", "Voltage")
c.physics("es").feature("term_neg").set("V0", "-V_app")

# === 网格 ===
c.mesh().create("mesh1")
c.mesh("mesh1").create("ftri1", "FreeTri")
c.mesh("mesh1").run()

# === 求解 ===
model.java.study().create("std1")
model.java.study("std1").create("stat", "Stationary")
model.java.study("std1").run()

# === 输出目录（根据系统自动设置）===
import os
out_dir = os.path.join(os.path.expanduser("~"), "comsol-scripts", "results")
os.makedirs(out_dir, exist_ok=True)

# === 导出 ===
model.java.result().export().create("exp1", "Data")
model.java.result().export("exp1").set("data", "dset1")
model.java.result().export("exp1").set("expr", ["V", "es.normE", "es.Ex", "es.Ey"])
model.java.result().export("exp1").set("filename",
    os.path.join(out_dir, "output.txt").replace("\\", "/"))
model.java.result().export("exp1").run()

# === 保存 ===
model.save(os.path.join(out_dir, "template_2d.mph").replace("\\", "/"))
model.clear()
client.remove(model)
print("DONE")
