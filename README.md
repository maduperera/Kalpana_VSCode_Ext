# ⚡ Kalpanā AI — Infinite Context Local Code Assistant for VS Code

> **Visual Studio Code extension powered by Kalpanā Resonant Interference Field (RIF) engine with True $\mathcal{O}(1)$ Continuous Fourier Phase Attention.**

---

## 🌟 Overview

**Kalpanā AI** is a next-generation local code assistant for Visual Studio Code that breaks through traditional dynamic KV cache memory limits. By superimposing workspace context onto a **fixed 48.00 MB continuous Fourier harmonic phase state**, Kalpanā provides infinite-context code reasoning without dynamic VRAM bloat.

- **Strict $\mathcal{O}(1)$ Attention Memory Footprint**: Locked at 48 MB, regardless of whether your project context is 1,000 or 3,000,000+ tokens.
- **100% Local Privacy**: Runs directly on your device with native SIMD acceleration.
- **Integrated Sidebar Chat UI**: Instant access to your workspace knowledge directly from the VS Code Activity Bar.

---

## 🚀 How to Install & Use in VS Code

### Option A: Local Developer / Debug Mode (Fastest)

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
   - Open the cloned folder in Visual Studio Code: `code .`
   - Press **`F5`** (or navigate to **Run and Debug** $\rightarrow$ **Launch Extension**).
   - A new *Extension Development Host* window will open.

4. **Access Kalpanā AI Sidebar**:
   - Click the **Kalpanā AI** icon (`🤖`) on the left Activity Bar sidebar.
   - Start chatting and asking questions about your codebase!

---

### Option B: Package and Install `.vsix` Extension

To generate a standalone `.vsix` extension package to share with team members or install permanently:

1. **Install VS Code Extension Packaging Tool (`vsce`)**:
   ```bash
   npm install -g @vscode/vsce
   ```

2. **Package the Extension**:
   ```bash
   vsce package
   ```
   *This compiles the TypeScript code and bundles the extension into `kalpana-ide-1.0.0.vsix` while automatically excluding uncompiled source files via `.vscodeignore`.*

3. **Install into VS Code**:
   - Open VS Code.
   - Press `Cmd + Shift + P` (or `Ctrl + Shift + P` on Windows/Linux).
   - Type **`Extensions: Install from VSIX...`** and select `kalpana-ide-1.0.0.vsix`.
   - Click **Install**.

---

## 🏛 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            VS Code Extension                                │
│       Sidebar Chat Webview (`kalpanaChatView`) & Engine Lifecycle           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / IPC
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 Kalpanā RIF Engine (Native C-Extension)                     │
│   • OpenAI-compatible API (`/v1/chat/completions`, `/v1/rif/ingest`)        │
│   • Native C++ / SIMD Fourier Phase Attention Core                           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Native Inference Backend (`llama-server`)                 │
│   • Local GGUF Model Execution (e.g., Qwen-2.5-Coder-7B / Llama-3.2-3B)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Project Structure

```
.
├── kalpana-engine/            # RIF Core Engine (Native C/Python FastAPI Gateway)
│   ├── api_server.py          # OpenAI-compatible API Server
│   ├── core.cpython-39-*.so   # Compiled Native Machine Code Module
│   ├── setup_cython.py        # Cython compilation specification
│   └── setup_server.sh        # Deployment helper script
├── src/                       # Extension TypeScript Source
│   └── extension.ts           # Extension entrypoint & Webview Provider
├── package.json               # VS Code extension manifest & contributions
├── tsconfig.json              # TypeScript compiler configuration
└── .vscodeignore              # Security rules excluding raw python source files
```

---

## 🔒 Security & Intellectual Property Protection

The core RIF mathematical attention layer is compiled directly into native C-extensions (`.so` / `.pyd` shared machine code libraries) with `-O3` compiler optimizations, protecting underlying algorithms from reverse-engineering or decompilation.

---

## 📄 License

Proprietary — All rights reserved. Kalpanā Series & RIF Architecture Technology.
