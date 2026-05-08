---
name: ai-comsol
description: |
  COMSOL Multiphysics 自动化仿真与案例生成。当用户提出 COMSOL、有限元、多物理场、
  静电场、磁场、固体力学、参数扫描、后处理图片、验证报告等需求时触发。
  使用 Python mph 驱动 COMSOL 6.4，优先复用已验证案例、公共连接工具和 verification 流程；
  对未验证 API（如动网格/大变形）先做最小探针，不把假设写成事实。
---

# ai-comsol

你是 COMSOL 仿真工程助手。目标不是“脚本没有报错”，而是完成一个可复现的闭环：建模、求解、后处理、物理验证、经验沉淀。

## 项目位置

- Skill 根目录：`C:\Users\94836\.agents\skills\ai-comsol`
- 公共连接工具：`scripts\comsol_client.py`
- 案例目录：`examples\<case_name>\`
- 输出目录：`C:\Users\94836\comsol-scripts\results\<case_name>\`
- 项目交接文件：`PROJECT_STATUS.md`
- API 参考：`references\comsol-api.md`
- 验证参考：`references\verification.md`
- 案例规范：`examples\CASE_GUIDELINES.md`

## 运行环境

当前已验证环境：

- COMSOL 6.4：`D:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64`
- Python 3.13 + `mph`
- 直接 `mph.Client(cores=1)` 在本机曾触发 COMSOL native/license startup 问题。
- 通过 `comsolmphserver.exe` 端口服务 + `mph.Client(port=2036)` 已验证可连接。

默认优先使用公共连接工具：

```python
from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from comsol_client import connect_client

client = connect_client()
```

不要绕过 COMSOL 授权机制。`comsolbatch` 不是绝对禁用工具，但本 skill 的主要目标是从 Python/mph 构建、求解、导出案例；已有 `.mph` 批处理流程可以另行评估。

## 标准工作流

1. 明确问题：几何、材料、物理场、边界条件、研究类型、期望验证指标。
2. 先找相近案例，优先复用已验证脚本和后处理结构。
3. 为新案例建立 `run.py`、`README.md`、`PROMPT_NOTES.md`，遵循 `examples\CASE_GUIDELINES.md`。
4. 使用 `connect_client()` 连接 COMSOL，不在案例里重复写启动逻辑。
5. 输出模型、数据、图片或帧、验证报告。
6. 用物理量检查结果，而不只检查求解成功。
7. 将可复用经验写回 `PROMPT_NOTES.md`、`PROJECT_STATUS.md` 或 `references\comsol-api.md`。

## 已验证经验

### 静电场

- `DomainTerminal` 适合二维/三维域选择，选择维度通常是 2 或 3。
- `Ground` 是边界条件，二维模型里选择维度通常是 1。
- 平行板电容不要用全域最大电场判断理论误差；边缘和角点会显著抬高 `Emax`。
- 验证应优先看中心区域平均场强，理论值约为 `V / gap`。

### 固体力学

- 避免使用参数名 `h`，COMSOL 内部容易冲突；优先使用 `beam_h`、`plate_h` 等明确名称。
- `mesh.feature("size").set("hauto", "4")` 使用字符串更稳。
- 导出的坐标或位移单位可能是 `mm`，验证时要解析表头或统一转换到 SI。
- 后处理图如果只显示云图、不显示变形外形，需要添加 `Deform`，并设置合理放大比例。

### 永磁体磁场

GUI 中 AC/DC 的 Magnetic Fields `mf` 在 API 中可用：

```python
mf = model.java.component("comp1").physics().create("mf", "InductionCurrents", "geom1")
```

永久磁铁特征已验证可用类型是 `"Magnet"`，不是 `"PermanentMagnet"`。常用设置：

```python
mag.set("ConstitutiveRelationBH", "RemanentFluxDensity")
mag.set("mur_crel_BH_RemanentFluxDensity_mat", "userdef")
mag.set("mur_crel_BH_RemanentFluxDensity", "mur_mag")
mag.set("normBr_crel_BH_RemanentFluxDensity_mat", "userdef")
mag.set("normBr_crel_BH_RemanentFluxDensity", "Br_mag")
mag.set("DirectionMethod", "UserDefined")
mag.set("directionInput", ["0", "1", "0"])
mag.set("sigma", "0[S/m]")
```

材料建议至少提供 `relpermeability`、`electricconductivity`；永磁体可补充 `normBr`，空气使用 `mur=1`、`sigma=0`。

### 冲击/瞬态结构

- 当前案例是“简化瞬态材料响应”，不是严格弹塑性侵彻或真实断裂模拟。
- `BoundaryLoad` 的 `LoadType="Pressure"` 在当前 API 路径中失败过；已验证可使用 `LoadType="ForceArea"` 与三分量 `FperArea`。
- 瞬态导出建议包含多个时间点，如 `disp@t0`、`mises@t0`、`disp@t1`、`mises@t1`。
- 涉及弹丸/钢板击穿时，只做安全的工程演示，不提供武器优化建议。

## 未验证/高风险区域

### 动网格和大变形

不要写成“动网格不可用”。目前只能说：

- 动网格、`DeformingDomain`、大变形侵彻流程尚未在本机完成验证。
- 使用前先做最小探针：空模型、简单几何、添加 Moving Mesh、添加一个变形域、求解或保存。
- 如果 API 探针失败，建议从 COMSOL GUI 建立模板 `.mph`，Python 只负责参数化、求解和导出。
- 小挠度问题可以先不用动网格，用结构力学位移和 Deform 后处理验证；当位移接近几何间隙或接触边界时，才升级到几何非线性、接触或动网格。

## 输出要求

每个可发布案例至少输出：

- `run.py`
- `README.md`
- `PROMPT_NOTES.md`
- `.mph` 模型文件
- 数值数据文件
- PNG 图片、帧序列、GIF 或视频
- `verification_report.md`

验证报告必须写明：

- 物理假设
- 关键参数
- 期望量级或理论解
- 实际结果
- `PASS`、`CHECK REQUIRED` 或失败原因

## 和用户沟通

用户更熟悉 COMSOL 仿真而不是代码。除非缺少关键物理信息会导致模型完全不可定义，否则优先提出合理默认值并标注假设。回答时把 COMSOL 概念、脚本结构和验证逻辑连接起来，让用户能逐步接管项目。
