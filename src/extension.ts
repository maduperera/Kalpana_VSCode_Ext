import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';

let engineProcess: child_process.ChildProcess | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Kalpana IDE backend is now active.');

    // 1. Start the Kalpana compiled binary automatically
    startKalpanaEngine(context);

    // 2. Register the Sidebar Chat Webview
    const provider = new KalpanaChatViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('kalpanaChatView', provider)
    );

    // 3. Register a command to manually restart the engine
    let startCmd = vscode.commands.registerCommand('kalpana.start', () => {
        startKalpanaEngine(context);
    });
    context.subscriptions.push(startCmd);
}

function startKalpanaEngine(context: vscode.ExtensionContext) {
    if (engineProcess) {
        engineProcess.kill();
    }

    // Determine the binary path based on the OS
    const isWindows = process.platform === 'win32';
    // For local development, pointing to the dist folder. In production, this would be bundled.
    const binaryName = isWindows ? 'kalpana-engine-win.exe' : 'kalpana-engine-mac';
    const binaryPath = path.join(context.extensionPath, 'kalpana-engine', 'dist', binaryName);

    console.log(`Starting Kalpana Engine from: ${binaryPath}`);
    
    // Spawn the binary
    engineProcess = child_process.spawn(binaryPath, [], {
        cwd: context.extensionPath
    });

    engineProcess.stdout?.on('data', (data) => {
        console.log(`Kalpana Engine: ${data}`);
    });

    engineProcess.stderr?.on('data', (data) => {
        console.error(`Kalpana Engine Error: ${data}`);
    });

    engineProcess.on('close', (code) => {
        console.log(`Kalpana Engine exited with code ${code}`);
    });
    
    vscode.window.showInformationMessage('Kalpana Engine (O(1) memory) started locally!');
}

class KalpanaChatViewProvider implements vscode.WebviewViewProvider {
    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        webviewView.webview.options = {
            enableScripts: true,
        };

        webviewView.webview.html = this._getHtmlForWebview();
        
        // Listen to messages from the chat UI
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'askQuestion':
                    {
                        // In the future: We will send this query to localhost:8000/v1/chat/completions
                        vscode.window.showInformationMessage(`Kalpana received: ${data.value}`);
                        
                        // Send mock response back to UI
                        webviewView.webview.postMessage({
                            type: 'receiveAnswer',
                            value: `This is Kalpana answering from the O(1) memory field! (You asked: ${data.value})`
                        });
                        break;
                    }
            }
        });
    }

    private _getHtmlForWebview() {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kalpana Chat</title>
            <style>
                body { font-family: var(--vscode-font-family); padding: 10px; color: var(--vscode-foreground); }
                #chat-box { height: 300px; overflow-y: auto; border: 1px solid var(--vscode-panel-border); padding: 5px; margin-bottom: 10px; }
                .message { margin-bottom: 8px; }
                .user-message { color: var(--vscode-terminal-ansiCyan); }
                .ai-message { color: var(--vscode-terminal-ansiGreen); }
                input { width: 100%; padding: 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }
            </style>
        </head>
        <body>
            <h3>Kalpana RIF Chat</h3>
            <p style="font-size: 10px; color: gray;">Memory: O(1) Bounded State</p>
            <div id="chat-box"></div>
            <input type="text" id="question-input" placeholder="Ask about your massive codebase..." />
            
            <script>
                const vscode = acquireVsCodeApi();
                const input = document.getElementById('question-input');
                const chatBox = document.getElementById('chat-box');

                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const text = input.value;
                        chatBox.innerHTML += \`<div class="message user-message"><b>You:</b> \${text}</div>\`;
                        vscode.postMessage({ type: 'askQuestion', value: text });
                        input.value = '';
                    }
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'receiveAnswer') {
                        chatBox.innerHTML += \`<div class="message ai-message"><b>Kalpana:</b> \${message.value}</div>\`;
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                });
            </script>
        </body>
        </html>`;
    }
}

export function deactivate() {
    if (engineProcess) {
        engineProcess.kill();
    }
}
