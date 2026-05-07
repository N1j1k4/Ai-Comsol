# COMSOL API 速查（mph Python 库）

## 基础骨架

```python
import mph
client = mph.Client(cores=1)
model = client.create("模型名")

# ... 建模 ...

model.save(r"C:\Users\11695\comsol-scripts\results\xxx.mph")
model.clear()
client.remove(model)
```

## 几何（2D）

```python
model.java.component().create("comp1")
c = model.java.component("comp1")
c.geom().create("geom1", 2)
g = c.geom("geom1")
g.lengthUnit("cm")  # 或 "um", "mm"

# 矩形（相邻不重叠 → 域编号等于创建顺序）
g.create("tag", "Rectangle")
g.feature("tag").set("size", ["宽度", "高度"])
g.feature("tag").set("pos", ["x0", "y0"])

g.run()  # 自动 FormUnion，不要手动创建
```

### 几何（3D）

```python
c.geom().create("geom1", 3)
g = c.geom("geom1"); g.lengthUnit("um")

g.create("tag", "Block")
g.feature("tag").set("size", ["Lx", "Ly", "Lz"])
g.feature("tag").set("pos", ["x0", "y0", "z0"])
g.run()
```

### ⚠️ 3D 几何注意事项
- 重叠矩形的 FormUnion 结果域编号不可预测
- 若必须做复杂 3D 几何，考虑用 GUI 建模板

## 材料

```python
c.material().create("tag", "Common")
c.material("tag").propertyGroup("def").set("relpermittivity", "3.5")     # 相对介电常数
c.material("tag").propertyGroup("def").set("youngsmodulus", "170e9[Pa]") # 杨氏模量（仅固力）
c.material("tag").propertyGroup("def").set("poissonsratio", "0.28")      # 泊松比（仅固力）
c.material("tag").propertyGroup("def").set("density", "2329[kg/m^3]")    # 密度（仅固力）
c.material("tag").selection().set([域号1, 域号2])
```

### 材料与固体力学的选区关系
- 只给需要受力分析的域赋 E/nu
- 其余域只赋 relpermittivity（或不赋材料）
- 没有 E 的域会被固体力学自动排除

## 物理场

### 静电场（es）

```python
c.physics().create("es", "Electrostatics", "geom1")

# 域终端——用于导体域（dim=2 在 2D, dim=3 在 3D）
c.physics("es").feature().create("term1", "DomainTerminal", 2)
c.physics("es").feature("term1").selection().set([域号])
c.physics("es").feature("term1").set("TerminalType", "Voltage")
c.physics("es").feature("term1").set("V0", "1000[V]")

# 接地——边界级特征（dim=1 在 2D, dim=2 在 3D）
c.physics("es").feature().create("gnd1", "Ground", 1)
c.physics("es").feature("gnd1").selection().set([边界号])
```

### 固体力学（solid）

```python
c.physics().create("solid", "SolidMechanics", "geom1")

# 固定约束（边界级，dim=1 在 2D, dim=2 在 3D）
c.physics("solid").feature().create("fix1", "Fixed", 1)
c.physics("solid").feature("fix1").selection().set([边界号])
```

### 多物理场耦合

```python
c.multiphysics().create("eme1", "ElectromechanicalForces", "geom1", 3)
```

## 动网格（DeformingDomain）— 当前无法从零创建

⚠️ **已知限制：** `c.common().create("df1", "DeformingDomain")` 报错需要坐标系。
当前只能通过 GUI 预建 .mph 模板来使用动网格。

## 网格

```python
# 2D
c.mesh().create("mesh1")
c.mesh("mesh1").create("ftri1", "FreeTri")
c.mesh("mesh1").run()

# 3D
c.mesh().create("mesh1")
c.mesh("mesh1").create("ftet1", "FreeTet")
c.mesh("mesh1").run()
```

## 求解

```python
model.java.study().create("std1")
model.java.study("std1").create("stat", "Stationary")
model.java.study("std1").run()
```

### 参数扫描

```python
model.java.param().set("V0", "100[V]", "电压")
model.java.study("std1").feature("stat").set("pname", ["V0"])
model.java.study("std1").feature("stat").set("plistarr", ["range(100,100,1000)"])
```

## 导出数据

```python
model.java.result().export().create("exp1", "Data")
model.java.result().export("exp1").set("data", "dset1")
model.java.result().export("exp1").set("expr", ["V", "es.normE", "es.Ex", "es.Ey"])
model.java.result().export("exp1").set("filename", "C:/Users/11695/comsol-scripts/results/out.txt")
model.java.result().export("exp1").run()
```

## ⚠️ 导出数据列索引（最易出错！）

导出文件格式：`x y z expr1 expr2 ...`

**2D（x, y 两列空间坐标）：**
| 列索引 | 含义 |
|--------|------|
| [0] | x |
| [1] | y |
| [2] | expr1 (V) |
| [3] | expr2 (es.normE) |

**3D（x, y, z 三列空间坐标）：**
| 列索引 | 含义 |
|--------|------|
| [0] | x |
| [1] | y |
| [2] | z |
| [3] | expr1 (V) |
| [4] | expr2 (u) |

**带参数扫描：** 每个参数步会追加一组表达式列

示例：2D 读 V 和 E
```python
for l in data_lines:
    if l[0].isdigit() or l[0] == '-':
        p = l.split()
        V = float(p[2])   # 列2
        E = float(p[3])   # 列3
```

## 常见错误速查

| 错误信息 | 原因 | 解决 |
|----------|------|------|
| "未知的几何操作" | 手动创建了 FormUnion/Finalize | 删除，只保留 `g.run()` |
| "不可编辑选择" | 试图修改自动特征的选区 | 不赋值 E 给非固力域，让 auto-filter 处理 |
| "未定义材料属性 E/nu" | 域没有弹性参数 | 补充材料属性，或删除该域上的固力 |
| "需要指定有效的坐标系" | DeformingDomain API 限制 | 用 GUI 模板 |
| V_max 异常大 | 读错列索引 | 2D 读 [2] 不是 [3]，3D 读 [3] 不是 [4] |
| DomainTerminal 不生效 | 用了 boundary dim 而非 domain dim | 2D 用 dim=2，3D 用 dim=3 |
