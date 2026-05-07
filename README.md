# ⚡ AI-COMSOL

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![COMSOL](https://img.shields.io/badge/COMSOL-6.4-orange)](https://comsol.com)
[![OpenCode](https://img.shields.io/badge/OpenCode-Skill-green)](https://opencode.ai)
[![mph](https://img.shields.io/badge/mph-1.3-lightgrey)](https://pypi.org/project/mph/)

**🌐 Language:** `[English](#english)` | `[中文](#中文)`

---

<h2 id="english">🇺🇸 English</h2>

> OpenCode skill for COMSOL 6.4 — describe your simulation in natural language, AI handles the rest.

### 🚀 What It Does

```
User: "Simulate a parallel-plate capacitor, 5cm gap, ±1000V"
  ↓
AI:  geometry → materials → physics → mesh → solve → verify
  ↓
Output: .mph model + numerical results + validation report
```

**Supported physics:** Electrostatics · Solid Mechanics · Electromechanical coupling

### 📦 Install

```bash
# 1. mph (Python COMSOL bridge)
pip install mph

# 2. Install skill
git clone https://github.com/N1j1k4/Ai-Comsol.git
Copy-Item -Recurse Ai-Comsol\skill\ai-comsol $env:USERPROFILE\.agents\skills\ai-comsol

# 3. Restart OpenCode
```

### 🎯 Examples

| Prompt | Result |
|--------|--------|
| "Parallel plate capacitor, 5cm gap, ±1000V" | V/E field distribution + verification |
| "Silicon cantilever 2cm×0.1cm, 1kN/m² load" | Displacement + stress |
| "Electrostatic actuator, 200μm gap, 100V" | Coupled electro-mechanical |

### 🛠️ Architecture

```
Prompt → OpenCode (ai-comsol skill) → Python mph → COMSOL 6.4 → Results
```

---

<h2 id="中文">🇨🇳 中文</h2>

> COMSOL 6.4 的 OpenCode 技能 — 用自然语言描述仿真需求，AI 自动完成全流程。

### 🚀 功能

```
用户: "仿真一个平行板电容器，间隙 5cm，±1000V"
  ↓
AI:  几何建模 → 材料分配 → 物理场 → 网格 → 求解 → 验证
  ↓
输出: .mph 模型 + 数值结果 + 验收报告
```

**支持物理场：** 静电场 · 固体力学 · 力电耦合

### 📦 安装

```bash
# 1. 安装 mph（Python 驱动 COMSOL）
pip install mph

# 2. 安装技能
git clone https://github.com/N1j1k4/Ai-Comsol.git
Copy-Item -Recurse Ai-Comsol\skill\ai-comsol $env:USERPROFILE\.agents\skills\ai-comsol

# 3. 重启 OpenCode
```

### 🎯 使用示例

| 描述 | 输出 |
|------|------|
| "平行板电容器，间隙 5cm，±1000V" | 电压/电场分布 + 自动验证 |
| "硅悬臂梁 2cm×0.1cm，1kN/m² 载荷" | 位移 + 应力 |
| "静电驱动器，间隙 200μm，偏压 100V" | 力电耦合位移 |

### 🛠️ 架构

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

*Built for fun. Will update in spare time.* ⚡
*闲暇之作，有空更新。* ⚡
