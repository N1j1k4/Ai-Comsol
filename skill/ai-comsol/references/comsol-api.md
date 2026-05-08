# COMSOL API 速查（mph Python 库）

这份文档给 `ai-comsol` skill 提供稳定的建模 recipe。优先使用这里的短代码模式，不要从乱码笔记或未验证片段里复制代码。

## 基础骨架

```python
import os
import mph

client = mph.Client(cores=1)
model = client.create("ModelName")

# ... 建模、网格、求解、导出 ...

out_dir = os.path.join(os.path.expanduser("~"), "comsol-scripts", "results")
os.makedirs(out_dir, exist_ok=True)
model.save(os.path.join(out_dir, "model.mph").replace("\\", "/"))

model.clear()
client.remove(model)
```

注意：
- Windows 路径传给 COMSOL Java API 时，优先使用 `.replace("\\", "/")`。
- 模型名、tag 名尽量使用英文、数字、下划线，避免中文 tag 造成 API 或编码问题。
- 脚本失败时，不要立刻改物理模型；先确认 COMSOL 能启动、license 可用、`mph.Client()` 能创建模型。

## 几何（2D）

```python
model.java.component().create("comp1")
c = model.java.component("comp1")
c.geom().create("geom1", 2)
g = c.geom("geom1")
g.lengthUnit("cm")  # 可改为 "um", "mm", "m"

g.create("rect1", "Rectangle")
g.feature("rect1").set("size", ["5", "1"])
g.feature("rect1").set("pos", ["0", "0"])

g.run()
```

几何规则：
- 简单案例优先 2D，便于调试选择和边界条件。
- 多个矩形尽量相邻或分离，避免不必要的重叠布尔操作。
- 不要手动创建 `FormUnion` 或 `Finalize`。通常 `g.run()` 会处理几何终结。
- 不要长期依赖“域编号一定等于创建顺序”。简单 2D 例子中可以临时使用编号，但复杂几何必须检查域和边界。

## 几何（3D）

```python
model.java.component().create("comp1")
c = model.java.component("comp1")
c.geom().create("geom1", 3)
g = c.geom("geom1")
g.lengthUnit("um")

g.create("blk1", "Block")
g.feature("blk1").set("size", ["10", "5", "1"])
g.feature("blk1").set("pos", ["0", "0", "0"])

g.run()
```

3D 注意事项：
- 3D 几何的域/边界编号更容易变化。必须通过可视化、导出检查或选择集验证。
- 复杂 3D CAD、重叠实体、阵列结构，建议先用 COMSOL GUI 建模，再由脚本参数化。

## 参数

```python
model.java.param().set("V_app", "1000[V]", "Applied voltage")
model.java.param().set("gap", "1[cm]", "Electrode gap")
model.java.param().set("eps_r", "1", "Relative permittivity")
```

建议：
- 所有带量纲参数都写单位，如 `"1000[V]"`、`"1[um]"`。
- 参数名使用英文，例如 `V_app`、`gap`、`beam_L`。

## 材料

```python
c.material().create("mat_air", "Common")
c.material("mat_air").propertyGroup("def").set("relpermittivity", "1")
c.material("mat_air").selection().set([1])

c.material().create("mat_si", "Common")
c.material("mat_si").propertyGroup("def").set("relpermittivity", "11.7")
c.material("mat_si").propertyGroup("def").set("youngsmodulus", "170e9[Pa]")
c.material("mat_si").propertyGroup("def").set("poissonsratio", "0.28")
c.material("mat_si").propertyGroup("def").set("density", "2329[kg/m^3]")
c.material("mat_si").selection().set([2])
```

材料规则：
- 静电场至少需要相对介电常数 `relpermittivity`。
- 固体力学通常需要 `youngsmodulus`、`poissonsratio`、`density`。
- 不参与固体力学的空气域不要乱加弹性参数。

## 静电场（Electrostatics）

```python
c.physics().create("es", "Electrostatics", "geom1")

# 导体域电压。2D 的域维度是 2，3D 的域维度是 3。
c.physics("es").feature().create("term1", "DomainTerminal", 2)
c.physics("es").feature("term1").selection().set([2])
c.physics("es").feature("term1").set("TerminalType", "Voltage")
c.physics("es").feature("term1").set("V0", "1000[V]")

# 接地通常是边界条件。2D 的边界维度是 1，3D 的边界维度是 2。
c.physics("es").feature().create("gnd1", "Ground", 1)
c.physics("es").feature("gnd1").selection().set([5])
```

关键规则：
- `DomainTerminal` 是域级特征。2D 用 `dim=2`，3D 用 `dim=3`。
- `Ground` 是边界级特征。2D 用 `dim=1`，3D 用 `dim=2`。
- 若电场处处为 0，先检查两个导体是否被设成同电位，或是否缺少参考地。

## 固体力学（Solid Mechanics）

```python
c.physics().create("solid", "SolidMechanics", "geom1")

# 固定约束是边界级特征。2D 用 dim=1，3D 用 dim=2。
c.physics("solid").feature().create("fix1", "Fixed", 1)
c.physics("solid").feature("fix1").selection().set([1])
```

关键规则：
- 固体力学必须有足够约束，否则会出现刚体位移或求解奇异。
- 空气域通常不参与固体力学。
- 位移方向要用物理直觉检查，例如静电力应拉向相反电极。

## 力电耦合

```python
c.multiphysics().create("eme1", "ElectromechanicalForces", "geom1", 3)
```

注意：
- 小变形静电驱动可以先忽略动网格，用静电力耦合固体力学验证趋势。
- 大变形、位移接近间隙、需要几何随位移更新时，通常需要 Moving Mesh / Deformed Geometry。
- 当前从零 API 创建 `DeformingDomain` 不稳定，建议使用预建 `.mph` 模板，再由脚本修改参数并求解。

## 网格

2D：

```python
c.mesh().create("mesh1")
c.mesh("mesh1").create("ftri1", "FreeTri")
c.mesh("mesh1").run()
```

3D：

```python
c.mesh().create("mesh1")
c.mesh("mesh1").create("ftet1", "FreeTet")
c.mesh("mesh1").run()
```

建议：
- 第一版先用自动网格跑通。
- 若结果数量级异常，再加局部加密和网格收敛性检查。

## 求解

稳态：

```python
model.java.study().create("std1")
model.java.study("std1").create("stat", "Stationary")
model.java.study("std1").run()
```

频域：

```python
model.java.study().create("std1")
model.java.study("std1").create("freq", "Frequency")
model.java.study("std1").feature("freq").set("plist", "range(1,1,10)[kHz]")
model.java.study("std1").run()
```

参数扫描：

```python
model.java.param().set("V_app", "100[V]", "Applied voltage")
model.java.study().create("std1")
model.java.study("std1").create("stat", "Stationary")
model.java.study("std1").feature("stat").set("pname", ["V_app"])
model.java.study("std1").feature("stat").set("plistarr", ["range(100,100,1000)"])
model.java.study("std1").run()
```

## 导出数据

```python
export_path = os.path.join(out_dir, "field_data.txt").replace("\\", "/")

model.java.result().export().create("exp1", "Data")
model.java.result().export("exp1").set("data", "dset1")
model.java.result().export("exp1").set("expr", ["V", "es.normE", "es.Ex", "es.Ey"])
model.java.result().export("exp1").set("filename", export_path)
model.java.result().export("exp1").run()
```

导出文件常见格式：

```text
x y expr1 expr2 ...
```

或 3D：

```text
x y z expr1 expr2 ...
```

列索引：

| 情况 | 坐标列 | 第一个表达式 |
| --- | --- | --- |
| 2D | `[0] = x`, `[1] = y` | `[2]` |
| 3D | `[0] = x`, `[1] = y`, `[2] = z` | `[3]` |

读取示例：

```python
values = []
with open(export_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        parts = line.split()
        try:
            values.append([float(x) for x in parts])
        except ValueError:
            pass

v_values = [row[2] for row in values]  # 2D 且 expr[0] = V
e_values = [row[3] for row in values]  # 2D 且 expr[1] = es.normE
```

## 二维绘图组与图片导出

```python
image_path = os.path.join(out_dir, "electric_field.png").replace("\\", "/")

model.java.result().create("pg_e", "PlotGroup2D")
model.java.result("pg_e").label("Electric field norm")
model.java.result("pg_e").feature().create("surf_e", "Surface")
model.java.result("pg_e").feature("surf_e").set("expr", "es.normE")
model.java.result("pg_e").feature("surf_e").set("unit", "V/m")
model.java.result("pg_e").run()

model.java.result().export().create("img_e", "pg_e", "Image")
model.java.result().export("img_e").set("imagetype", "png")
model.java.result().export("img_e").set("pngfilename", image_path)
model.java.result().export("img_e").set("width", "1200")
model.java.result().export("img_e").set("height", "800")
model.java.result().export("img_e").set("unit", "px")
model.java.result().export("img_e").set("options2d", "on")
model.java.result().export("img_e").set("title2d", "on")
model.java.result().export("img_e").set("legend2d", "on")
model.java.result().export("img_e").run()
```

建议：
- 静电场图片优先导出 `es.normE`，用于检查边缘场和中心区域是否合理。
- 电势图片可另建一个 `PlotGroup2D`，表达式使用 `V`。
- 如果图片导出失败，先确认模型已经求解，并且对应 plot group 已经 `run()`。

## 常见错误速查

| 现象 / 报错 | 常见原因 | 处理 |
| --- | --- | --- |
| `mph.Client()` 失败 | COMSOL 未安装、license 不可用、版本不匹配 | 先跑环境预检，确认 COMSOL GUI 能打开 |
| 未知几何操作 | 手动创建了不兼容的 `FormUnion` / `Finalize` | 删除手动终结操作，只保留 `g.run()` |
| 选择不可编辑 | 试图修改自动生成特征的选择 | 新建自己的 feature 或 selection |
| 材料属性未定义 | 固体域缺少 `E` / `nu` / `density` | 补材料，或把该域排除出固体力学 |
| `DomainTerminal` 不生效 | 把域级特征当边界级特征使用 | 2D 用 `dim=2`，3D 用 `dim=3` |
| 接地不生效 | 边界编号选错或维度错 | 2D Ground 用 `dim=1`，3D 用 `dim=2` |
| 电压全是常数 | 缺少参考地或所有导体同电位 | 增加 Ground 或设置不同电位 |
| 电场数量级错 | 单位、间隙、导出列索引错误 | 用 `E ≈ V / d` 快速验算 |
| 固体位移为 0 | 固定边界选错、力未耦合、材料/选择错误 | 检查 solid 域、固定端、耦合项 |
| 求解不收敛 | 约束不足、网格太粗、非线性太强 | 先简化模型，再逐步加物理场 |
| Moving Mesh 创建失败 | 从零 API 创建动网格不稳定 | 用 GUI 预建模板，再脚本参数化 |

## 建议工作流

1. 先跑最小模型：几何、材料、物理场、网格、稳态。
2. 导出最少结果：`V`、`es.normE`，或固体位移。
3. 用理论量级验算：平行板 `E ≈ V / d`，悬臂梁 `δ ≈ F L^3 / (3 E I)`。
4. 通过后再加参数扫描、复杂几何、多物理场耦合。
5. 每个案例保留 `run.py`、`results/`、`verification_report.md`，方便复现。
