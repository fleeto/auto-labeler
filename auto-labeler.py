#!/usr/bin/env python3
import argparse
import os
import sys
import json
import subprocess

parser = argparse.ArgumentParser(description='Pod hook for Shell-Operator')
parser.add_argument('--config', action='store_true')

args = parser.parse_args()
CONFIG_FILE = os.getenv("CONFIG_FILE", "/etc/auto-labeler/config.yaml")
CONTEXT_FILE = os.getenv("BINDING_CONTEXT_PATH")
COPY_LABELS = os.getenv("COPY_LABELS", "node-dc,node-rack,node-name")

if args.config:
    with open(CONFIG_FILE) as cfg:
        print("".join(cfg.readlines()))
    sys.exit(0)

context = None
print("Processing context file: ", CONTEXT_FILE)
with open(CONTEXT_FILE) as context_hdl:
    context = json.load(context_hdl)

if context[0]["type"] == "Synchronization":
    print("Garbage fired.")
    sys.exit(0)

for item in context:
    obj = item["object"]

    node_name = obj["spec"]["nodeName"]
    namespace = obj["metadata"]["namespace"]
    pod_name = obj["metadata"]["name"]
    print("Processing {}...".format(pod_name))

    node_info = json.loads(
        subprocess.check_output(
            ["kubectl", "get", "node", node_name, "-o", "json"]))

    node_labels = node_info["metadata"]["labels"]
    copy_keys = COPY_LABELS.split(",")

    final_labels = []
    for key in [key for key in node_labels.keys() if key in copy_keys]:
        final_labels.append("{}={}".format(key, node_labels[key]))
    cmd = ["kubectl", "label", "pods", pod_name,  "-n", namespace] + final_labels
    print(cmd)
    print(subprocess.check_output(cmd))
sys.exit(0)
