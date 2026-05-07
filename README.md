# ⚡ AI-COMSOL

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![COMSOL](https://img.shields.io/badge/COMSOL-6.4-orange)](https://comsol.com)
[![OpenCode](https://img.shields.io/badge/OpenCode-MCP-green)](https://opencode.ai)

> AI-driven full-automatic simulation via OpenCode MCP + COMSOL 6.4

---

## 🚀 Features

| Category | Support |
|----------|---------|
| **3D Geometry** | Block, Cylinder, Sphere, Air Box |
| **Physics** | MF / MFNC / MEF / ES / EC / HT / Solid |
| **Magnetization** | Br + Mur + direction for PM |
| **Mesh** | Auto 5-level (finer → coarser) |
| **Study** | Stationary / Frequency / Time / Eigen |
| **Results** | Expression & global matrix eval |

Powered by **DeepSeek-V4-Pro**. Just for fun — will update in spare time.

---

## 📦 Install

```bash
npm i -g opencode-ai
pip install fastmcp
```

Add to `~/.config/opencode/opencode.json`:
```json
{
  "mcp": {
    "comsol": {
      "type": "local",
      "command": ["python", "path/to/comsol_mcp_server.py"],
      "enabled": true
    }
  }
}
```

---

## 🎯 Usage

```
"Simulate a 10×5×2mm NdFeB magnet, Br=1.44T Z-axis"
```

Auto workflow:
```
comsol_new → comsol_block → comsol_airbox → comsol_physics(mfnc)
→ comsol_magnetize → comsol_mesh → comsol_study → comsol_eval
```

Result: **Max B = 1.44 T**

---

## 🛠️ Architecture

```
OpenCode → MCP → Python → COMSOL java.exe → COMSOL Java API
```

---

*Just for fun. Will update in spare time.* ⚡
