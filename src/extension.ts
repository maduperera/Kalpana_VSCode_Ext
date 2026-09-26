import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';

let engineProcess: child_process.ChildProcess | undefined;
let llamaProcess: child_process.ChildProcess | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Kalpana IDE backend is now active.');

    // 1. Start the backend engines (Llama.cpp + Kalpana RIF)
    startEngines(context);

    // 2. Register the Sidebar Chat Webview
    const provider = new KalpanaChatViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('kalpanaChatView', provider)
    );

    // 3. Register a command to manually restart the engines
    let startCmd = vscode.commands.registerCommand('kalpana.start', () => {
        startEngines(context);
    });
    context.subscriptions.push(startCmd);
}

function startEngines(context: vscode.ExtensionContext) {
    if (engineProcess) engineProcess.kill();
    if (llamaProcess) llamaProcess.kill();

    const isWindows = process.platform === 'win32';
    const isMac = process.platform === 'darwin';

    // --- STEP 1: Launch Kalpana Python API (RIF State Manager) ---
    const pythonBinary = isWindows ? 'kalpana-engine-win.exe' : 'kalpana-engine-mac';
    const pythonBinaryPath = path.join(context.extensionPath, 'kalpana-engine', 'dist', pythonBinary);
    const apiServerPath = path.join(context.extensionPath, 'kalpana-engine', 'api_server.py');
    
    if (fs.existsSync(pythonBinaryPath)) {
        engineProcess = child_process.spawn(pythonBinaryPath, [], { cwd: context.extensionPath });
        engineProcess.stdout?.on('data', (data: Buffer | string) => console.log(`Kalpana API: ${data}`));
    } else if (fs.existsSync(apiServerPath)) {
        const pythonExec = isWindows ? 'python' : 'python3';
        engineProcess = child_process.spawn(pythonExec, [apiServerPath], { cwd: context.extensionPath });
        engineProcess.stdout?.on('data', (data: Buffer | string) => console.log(`Kalpana API: ${data}`));
    } else {
        vscode.window.showWarningMessage('Kalpana RIF Engine server not found.');
    }

    // --- STEP 2: Launch Llama.cpp backend (The Text Generator) ---
    // In production, the extension will download the pre-compiled llama-server for Win/Mac.
    // We assume it's downloaded to an 'inference' folder.
    const llamaBinary = isWindows ? 'llama-server.exe' : 'llama-server';
    const llamaPath = path.join(context.extensionPath, 'inference', llamaBinary);
    const modelPath = path.join(context.extensionPath, 'models', 'Qwen-2.5-Coder-7B-Q4.gguf');

    if (fs.existsSync(llamaPath) && fs.existsSync(modelPath)) {
        llamaProcess = child_process.spawn(llamaPath, [
            '-m', modelPath,
            '--host', '127.0.0.1',
            '--port', '8081',
            '-c', '4096' // Standard context fallback
        ], { cwd: context.extensionPath });
        llamaProcess.stdout?.on('data', (data: Buffer | string) => console.log(`Llama.cpp: ${data}`));
    } else {
        console.log('Llama.cpp binary or model not found yet. Ready for download phase.');
    }
    
    vscode.window.showInformationMessage('Kalpana Backend initialized locally.');
}

class KalpanaChatViewProvider implements vscode.WebviewViewProvider {
    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(webviewView: vscode.WebviewView, context: vscode.WebviewViewResolveContext) {
        webviewView.webview.options = { enableScripts: true };
        webviewView.webview.html = this._getHtmlForWebview();
        
        webviewView.webview.onDidReceiveMessage(async (data: any) => {
            if (data.type === 'askQuestion') {
                // Here we will eventually send the query to http://127.0.0.1:8000/v1/chat/completions
                webviewView.webview.postMessage({
                    type: 'receiveAnswer',
                    value: `Processing via O(1) Memory Engine: ${data.value}`
                });
            }
        });
    }

    private _getHtmlForWebview() {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <style>
                body { font-family: var(--vscode-font-family); padding: 10px; color: var(--vscode-foreground); }
                #chat-box { height: 350px; overflow-y: auto; border: 1px solid var(--vscode-panel-border); padding: 5px; margin-bottom: 10px; }
                .message { margin-bottom: 8px; font-size: 13px; }
                .user-message { color: var(--vscode-terminal-ansiCyan); }
                .ai-message { color: var(--vscode-terminal-ansiGreen); }
                input { width: 100%; padding: 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }
            </style>
        </head>
        <body>
            <h3>Kalpana (Qwen-7B RIF)</h3>
            <div id="chat-box"></div>
            <input type="text" id="question-input" placeholder="Ask about your workspace..." />
            <script>
                const vscode = acquireVsCodeApi();
                const input = document.getElementById('question-input');
                const chatBox = document.getElementById('chat-box');
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        chatBox.innerHTML += \`<div class="message user-message"><b>You:</b> \${input.value}</div>\`;
                        vscode.postMessage({ type: 'askQuestion', value: input.value });
                        input.value = '';
                    }
                });
                window.addEventListener('message', event => {
                    if (event.data.type === 'receiveAnswer') {
                        chatBox.innerHTML += \`<div class="message ai-message"><b>Kalpana:</b> \${event.data.value}</div>\`;
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                });
            </script>
        </body>
        </html>`;
    }
}

export function deactivate() {
    if (engineProcess) engineProcess.kill();
    if (llamaProcess) llamaProcess.kill();
}
