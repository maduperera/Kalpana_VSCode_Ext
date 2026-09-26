# ⚡ Kalpanā AI — Infinite-Context Local Code Assistant for VS Code

> **The first Visual Studio Code assistant powered by Kalpanā Resonant Interference Field (RIF™) technology.**  
> **Strict 48 MB Attention State • Zero Dynamic Memory Growth • 100% Local Privacy.**

---

## 🌟 What is Kalpanā AI?

**Kalpanā AI** is a revolutionary AI coding assistant built for Visual Studio Code. Traditional AI code assistants slow down or crash your computer when working with large codebases because their memory consumption scales linearly with project size.

Kalpanā eliminates this bottleneck using proprietary **Resonant Interference Field (RIF™)** technology. Instead of storing massive token histories in RAM, Kalpanā maintains a **strict $\mathcal{O}(1)$ constant 48 MB memory footprint**—allowing you to query entire multi-file codebases effortlessly on standard developer laptops without memory slowdowns or out-of-memory crashes.

---

## 🔥 Key Capabilities

* 🧠 **Infinite-Context Workspace Ingestion**: Feed massive project folders and documentation directly to the assistant without hitting memory walls.
* ⚡ **Strict $\mathcal{O}(1)$ Constant Memory**: Memory footprint remains locked at **~48 MB**, regardless of whether your project context contains 10,000 or 3,000,000+ tokens.
* 🔒 **100% Local & Confidential**: All inference runs locally on your machine. Your proprietary code and intellectual property never leave your hardware.
* 💻 **Seamless VS Code Integration**: Dedicated sidebar panel accessible directly from the VS Code Activity Bar (`🤖`).

---

## 📊 Performance & Memory Comparison

| Capability / Metric | Traditional AI Extensions | **Kalpanā AI (RIF™ Engine)** |
| :--- | :--- | :--- |
| **Attention Memory Growth** | Scales linearly $\mathcal{O}(N)$ up to 30+ GB | **Strict $\mathcal{O}(1)$ Flatline (~48 MB)** |
| **Large Codebase Behavior** | Slowdowns, RAM bloat & OOM crashes | **Instant, constant-memory execution** |
| **Local Hardware Overhead** | Requires expensive High-VRAM GPUs | **Runs smoothly on standard laptops** |
| **Data Privacy** | Cloud uploads / SaaS dependency | **100% On-Device Local Privacy** |

---

## 🚀 Installation & Quick Start

### 1. Developer Installation (Side-Load Mode)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/maduperera/Kalpana_VSCode_Ext.git
   cd Kalpana_VSCode_Ext
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Launch in VS Code**:
   - Open the folder in VS Code: `code .`
   - Press **`F5`** (or select **Run and Debug** $\rightarrow$ **Launch Extension**).

4. **Start Chatting**:
   - Click the **Kalpanā AI** icon (`🤖`) on the VS Code Activity Bar sidebar to start querying your codebase.

---

### 2. Package as `.vsix` Extension

To generate a standalone `.vsix` file to install on any VS Code machine:

```bash
# Install packaging CLI
npm install -g @vscode/vsce

# Package extension
vsce package
```

Then in VS Code, open **Command Palette** (`Cmd+Shift+P` / `Ctrl+Shift+P`) $\rightarrow$ **`Extensions: Install from VSIX...`** and select the `.vsix` file.

---

## 🏛 System Architecture Overview

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                      VS Code Sidebar Extension                          │
 │         Interactive Chat UI & Workspace Context Orchestrator            │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │ Local IPC / HTTP
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                    Kalpanā RIF™ State Engine                            │
 │     • Single Unified 48 MB Memory State (0.00 MB Dynamic Cache Growth)  │
 │     • Native SIMD Vectorized Inference Acceleration                     │
 └─────────────────────────────────────────────────────────────────────────┘
```

---

## 📄 License & Proprietary Notice

**Copyright © 2026 Kalpanā Series & RIF™ Architecture.** All rights reserved.  
*Kalpanā and Resonant Interference Field (RIF) are trademarks. Proprietary native core engine engine protected under compilation.*
