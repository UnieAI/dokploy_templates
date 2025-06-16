import os
import shutil
import re
import json

# Create output directory
os.makedirs("output", exist_ok=True)
os.makedirs("output/blueprints", exist_ok=True)

# Load list.txt
with open("list.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

meta_list = []

for line in lines:
    line = line.strip()
    if not line or ("," not in line and ";" not in line):
        continue

    # Allow both ',' and ';' as delimiters
    for sep in [',', ';']:
        if sep in line:
            model_path, image_name = line.split(sep)
            break

    # Extract model name and make folder name
    model_name = model_path.split('/')[-1]
    folder_name = re.sub(r"[.-]", "_", model_name)

    folder_path = os.path.join("output/blueprints", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Write docker-compose.yml
    docker_compose = f"""version: "3.8"

services:
  unieinfra:
    image: vllm/vllm-openai:latest
    runtime: nvidia  # Required for GPU access
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
    ports:
      - "8000"
    environment:
      - NCCL_SHM_DISABLE=1  # Bypass shared memory transport
      - NCCL_DEBUG=INFO  # Enable detailed error logging
    shm_size: "8gb"
    entrypoint: vllm
    command: ["serve", "{model_path}", "--served-model-name", "{folder_name}"]
"""
    with open(os.path.join(folder_path, "docker-compose.yml"), "w", encoding="utf-8") as f:
        f.write(docker_compose)

    # Write template.toml
    template_toml = f"""[variables]
main_domain = "${{domain}}"

[config]
env = []
mounts = []

[[config.domains]]
serviceName = "unieinfra"
port = 8000
host = "${{main_domain}}"
"""
    with open(os.path.join(folder_path, "template.toml"), "w", encoding="utf-8") as f:
        f.write(template_toml)

    # Copy PNG
    if os.path.exists(image_name):
        shutil.copy(image_name, os.path.join(folder_path, os.path.basename(image_name)))
    else:
        print(f"Warning: Image {image_name} not found.")

    # Add to meta.json structure
    meta_list.append({
        "id": folder_name,
        "name": model_name,
        "version": "0.0.0",
        "description": f"{model_name} model served via UnieInfra.",
        "logo": os.path.basename(image_name),
        "links": {
            "github": f"https://github.com",
            "website": f"https://huggingface.co/{model_path}",
            "docs": f"https://huggingface.co/{model_path}"
        },
        "tags": ["llm", "unieinfra"]
    })

# Write meta.json
with open("output/meta.json", "w", encoding="utf-8") as f:
    json.dump(meta_list, f, indent=2)

