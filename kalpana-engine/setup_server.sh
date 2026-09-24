#!/usr/bin/env bash
# ==============================================================================
# Kalpanā LLM Pro 1.1 - Automated Setup & Deployment Script
# Targets: Oracle Cloud ARM64 (Ampere A1 / Neoverse-N1) & Ubuntu Linux
# ==============================================================================
set -e

echo "=== [1/6] System Dependencies & Tools ==="
sudo apt-get update -y
sudo apt-get install -y build-essential cmake ninja-build git python3-pip python3-venv curl

echo "=== [2/6] Swap Space Setup (Ensures Stable Compilation) ==="
if [ ! -f /swapfile ]; then
    echo "Creating 16GB Swap File..."
    sudo fallocate -l 16G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo "=== [3/6] Compiling Native C++ llama-server with ARM NEON SIMD ==="
cd /home/ubuntu
if [ ! -d "/home/ubuntu/llama.cpp-clean" ]; then
    git clone https://github.com/ggml-org/llama.cpp.git llama.cpp-clean
fi
cd /home/ubuntu/llama.cpp-clean
cmake -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_NATIVE=ON \
    -DGGML_NEON=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=ON
cmake --build build --config Release -j $(nproc) --target llama-server llama-cli

echo "=== [4/6] Model Weights Preparation ==="
mkdir -p /home/ubuntu/models
if [ ! -f "/home/ubuntu/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf" ]; then
    echo "Downloading Llama-3.2-3B-Instruct-Q4_K_M.gguf..."
    curl -L -o /home/ubuntu/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
      "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
fi

echo "=== [5/6] Python Environment & Dependencies ==="
pip3 install --upgrade pip
pip3 install fastapi uvicorn httpx pydantic numpy requests

echo "=== [6/6] Registering & Starting Systemd Services ==="
sudo cp kalpana-cpp.service /etc/systemd/system/kalpana-cpp.service
sudo cp kalpana-api.service /etc/systemd/system/kalpana-api.service

sudo systemctl daemon-reload
sudo systemctl enable kalpana-cpp kalpana-api
sudo systemctl restart kalpana-cpp kalpana-api

sleep 3
echo "=== Deployment Complete! Verification Status ==="
sudo systemctl status kalpana-cpp --no-pager
sudo systemctl status kalpana-api --no-pager

echo ""
echo "Kalpana LLM Pro 1.1 is now running on:"
echo "Public API: http://$(curl -s ifconfig.me):8000/v1"
echo "Interactive Swagger Docs: http://$(curl -s ifconfig.me):8000/docs"
echo "Interactive Web Playground: http://$(curl -s ifconfig.me):8000/"
