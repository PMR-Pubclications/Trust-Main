#!/usr/bin/env python3
import sys
import os
import yaml

class LiteralString(str):
    """Custom str subclass to force YAML literal block scalar style (|)."""
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(LiteralString, literal_presenter)

def convert_sh_to_configmap(sh_filepath, output_filepath=None, cm_name="script-configmap"):
    if not os.path.exists(sh_filepath):
        print(f"Error: File '{sh_filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(sh_filepath, 'r', encoding='utf-8') as f:
        script_content = f.read()

    filename = os.path.basename(sh_filepath)

    config_map = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": cm_name
        },
        "data": {
            filename: LiteralString(script_content)
        }
    }

    yaml_output = yaml.dump(config_map, sort_keys=False, default_flow_style=False)

    if output_filepath:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_output)
        print(f"[SUCCESS] Wrote ConfigMap to {output_filepath}")
    else:
        print(yaml_output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sh2yaml.py <path_to_script.sh> [output.yaml] [configmap_name]")
        sys.exit(1)

    input_sh = sys.argv[1]
    output_yaml = sys.argv[2] if len(sys.argv) > 2 else None
    cm_name = sys.argv[3] if len(sys.argv) > 3 else "trust-shell-script"

    convert_sh_to_configmap(input_sh, output_yaml, cm_name)
