import time
import requests
import json

BASE_URL = "http://129.146.20.101:8000/v1"
API_KEY = "kalpana-sk-beta-eval"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print("=== 1. Testing Standard Non-Streaming Chat Completion ===")
payload = {
    "model": "kalpana-llama",
    "messages": [
        {"role": "system", "content": "You are Kalpana LLM, an AI assistant powered by True O(1) Continuous Fourier Phase Attention."},
        {"role": "user", "content": "Explain what Kalpana RIF is and why 48 MB fixed attention matters."}
    ],
    "max_tokens": 80,
    "temperature": 0.7
}

t0 = time.perf_counter()
resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
t1 = time.perf_counter()

if resp.status_code == 200:
    data = resp.json()
    print("Assistant Response:")
    print(data["choices"][0]["message"]["content"].strip())
    print("\nKalpana Telemetry:")
    print(json.dumps(data.get("kalpana_telemetry", {}), indent=2))
    print(f"Total API Latency: {t1 - t0:.2f} s")
else:
    print(f"Error {resp.status_code}: {resp.text}")

print("\n=== 2. Testing Streaming Chat Completion (SSE) ===")
payload["stream"] = True
t0 = time.perf_counter()
first_token_time = None
tokens = 0
stream_text = []

with requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                chunk_str = line_str[6:].strip()
                if chunk_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(chunk_str)
                    delta = chunk["choices"][0].get("delta", {}).get("content", "")
                    if delta:
                        if first_token_time is None:
                            first_token_time = time.perf_counter() - t0
                        tokens += 1
                        stream_text.append(delta)
                        print(delta, end="", flush=True)
                except Exception:
                    pass

total_stream_time = time.perf_counter() - t0
print("\n")
print(f"Time to First Token (TTFT): {(first_token_time*1000):.1f} ms" if first_token_time else "TTFT: N/A")
print(f"Tokens Received: {tokens}")
print(f"Total Stream Latency: {total_stream_time:.2f} s")
if first_token_time and (total_stream_time - first_token_time) > 0:
    tps = tokens / (total_stream_time - first_token_time)
    print(f"Streaming Speed: {tps:.2f} tokens/second")
