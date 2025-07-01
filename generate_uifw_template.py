import os
import yaml
from yaml.representer import SafeRepresenter

# 讓 command 欄位單獨以 flow style 列印
class FlowStyleList(list):
    pass

def flow_style_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowStyleList, flow_style_list_representer, Dumper=yaml.SafeDumper)

def model_to_service_name(model: str) -> str:
    name = model.split("/")[-1]
    name = name.replace("-", "_").replace(".", "_")
    # name = re.sub(r'([0-9])([A-Za-z])', r'\1_\2', name)
    return name.lower()

def model_to_folder_name(model: str) -> str:
    model_name = model.split("/")[-1]
    name = model_name.replace("-", "_").replace(".", "_")
    return f"{name}_uifw_NV"

def generate_docker_compose(service_name: str, model_repo: str, model_name: str):
    service = {
        "unieinfra": {
            "image": "registry.unieai.com/unieai/uifw2:357f1be",
            "volumes": ["./weight:/weight"],
            "ports": ["35640:35640"],
            "runtime": "nvidia",
            "environment": [
                "NCCL_SHM_DISABLE=1",
                "NCCL_DEBUG=INFO",
                "CUDA_VISIBLE_DEVICES=0",
                "HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN}"
            ],
            "shm_size": "8gb",
            "entrypoint": "uifw",
            "command": FlowStyleList([
                "serve", "api_server",  model_repo,
                "--server-port", "35640",
                "--log-level", "INFO",
                "--model-name", model_name,
                "--session-len", "1024", 
                "--dtype", "float16", 
                "--cache-max-entry-count", "0.1"
            ]),
            "deploy": {
                "resources": {
                    "reservations": {
                        "devices": [
                            {
                                "driver": "nvidia",
                                "capabilities": ["gpu"]
                            }
                        ]
                    }
                }
            }
        }
    }

    return yaml.dump({"version": "3.8", "services": service}, sort_keys=False, Dumper=yaml.SafeDumper)

def generate_template_toml(service_name: str) -> str:
    return f"""[variables]
main_domain = "${{domain}}"

[config]
env = []
mounts = []

[[config.domains]]
serviceName = "unieinfra"
port = 35640
host = "${{main_domain}}"

[config.env]
HUGGING_FACE_HUB_TOKEN="${{HUGGING_FACE_HUB_TOKEN}}"
"""

def main():
    models = [
        "meta-llama/Llama-3.1-8B-Instruct",
        "meta-llama/Llama-3.1-70B-Instruct",
        "mistral/Mixtral-8x7B-Instruct-v0.1",
        "meta-llama/Llama-3.2-11B-Vision"
    ]

    for model in models:
        service_name = model_to_service_name(model)
        folder_name = model_to_folder_name(model)
        model_name = model.split("/")[-1]

        os.makedirs(folder_name, exist_ok=True)

        with open(os.path.join(folder_name, "docker-compose.yml"), "w") as f:
            f.write(generate_docker_compose(service_name, model, model_name))

        with open(os.path.join(folder_name, "template.toml"), "w") as f:
            f.write(generate_template_toml(service_name))

        print(f"{folder_name} 完成")

if __name__ == "__main__":
    main()
