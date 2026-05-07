# ⚡ AI-COMSOL
*Built for fun. Will update in spare time.* ⚡
*娱乐之作，有空更新。* ⚡

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![COMSOL](https://img.shields.io/badge/COMSOL-6.4-orange)](https://comsol.com)
[![OpenCode](https://img.shields.io/badge/OpenCode-Skill-green)](https://opencode.ai)
[![mph](https://img.shields.io/badge/mph-1.3-lightgrey)](https://pypi.org/project/mph/)

**🌐** [English](#english) **|** [中文](#中文)

---

# English

> OpenCode skill for COMSOL 6.4 — describe your simulation in natural language, AI handles the rest.

## 🚀 What It Does

```
User: "Simulate a parallel-plate capacitor, 5cm gap, ±1000V"
  ↓
AI:  geometry → materials → physics → mesh → solve → verify
  ↓
Output: .mph model + numerical results + validation report
```

**Supported physics:** Electrostatics · Solid Mechanics · Electromechanical coupling

## 📦 Install

```bash
# 1. mph (Python COMSOL bridge)
pip install mph

# 2. Install skill
git clone https://github.com/N1j1k4/Ai-Comsol.git
Copy-Item -Recurse Ai-Comsol\skill\ai-comsol $env:USERPROFILE\.agents\skills\ai-comsol

# 3. Restart OpenCode
```

## 🎯 Examples

| Prompt | Result |
|--------|--------|
| "Parallel plate capacitor, 5cm gap, ±1000V" | V/E field distribution + verification |


## 🛠️ Architecture

```
Prompt → OpenCode (ai-comsol skill) → Python mph → COMSOL 6.4 → Results
```

---

# 中文

> COMSOL 6.4 的 OpenCode 技能 — 用自然语言描述仿真需求，AI 自动完成全流程。

## 🚀 功能

```
用户: "仿真一个平行板电容器，间隙 5cm，±1000V"
  ↓
AI:  几何建模 → 材料分配 → 物理场 → 网格 → 求解 → 验证
  ↓
输出: .mph 模型 + 数值结果 + 验收报告
```

**支持物理场：** 静电场 · 固体力学 · 力电耦合

## 📦 安装

```bash
# 1. 安装 mph（Python 驱动 COMSOL）
pip install mph

# 2. 安装技能
git clone https://github.com/N1j1k4/Ai-Comsol.git
Copy-Item -Recurse Ai-Comsol\skill\ai-comsol $env:USERPROFILE\.agents\skills\ai-comsol

# 3. 重启 OpenCode
```

## 🎯 使用示例

| 描述 | 输出 |
|------|------|
| "平行板电容器，间隙 5cm，±1000V" | 电压/电场分布 + 自动验证 |


## 🛠️ 架构

```
自然语言 → OpenCode (ai-comsol 技能) → Python mph → COMSOL 6.4 → 结果输出
```

---

## 📁 Project Structure / 项目结构

```
Ai-Comsol/
├── skill/ai-comsol/
│   ├── SKILL.md                     # Agent skill definition / 技能定义
│   ├── references/
│   │   ├── comsol-api.md            # mph API quick reference / API 速查
│   │   └── verification.md          # Self-verification guide / 自验收指南
│   └── scripts/
│       └── template_2d_es.py        # Parallel-plate capacitor template / 模板
├── comsol_mcp_server.py             # (Legacy) MCP subprocess server / 旧版
└── README.md
```

---

| Software | Version |
|----------|---------|
| COMSOL Multiphysics | 6.4 |
| Python | 3.9+ |
| mph | 1.3+ |
| OpenCode | latest |

---
## ⚠️ Disclaimer / 免责声明

- COMSOL Multiphysics® is a registered trademark of COMSOL AB. This project is **not** affiliated with, endorsed by, or sponsored by COMSOL AB.
- This project does **not** modify, decompile, or redistribute any COMSOL binaries or libraries. It requires a legally licensed copy of COMSOL to function.
- All simulation results should be independently verified. The authors assume no liability for any errors or damages arising from the use of this tool.
- This project is intended for educational and research purposes only.

---

- COMSOL Multiphysics® 是 COMSOL AB 的注册商标。本项目**与 COMSOL AB 无关**，未获其认可或赞助。
- 本项目**未**修改、反编译或再分发 COMSOL 的任何二进制文件或库。运行需要合法授权的 COMSOL 许可证。
- 所有仿真结果应独立验证。作者对因使用本工具产生的任何错误或损失不承担责任。
- 本项目仅供学习和研究用途。
