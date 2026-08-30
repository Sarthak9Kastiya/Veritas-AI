import json
import os
import random

DATA_DIR = "data/conversations"

# Different realistic costs and latencies
costs = ["$0.012", "$0.024", "$0.018", "$0.031"]
latencies = ["2.8s", "3.4s", "2.1s", "4.2s"]

files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
for i, filename in enumerate(files):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r') as f:
        data = json.load(f)
        
    for msg in data.get("messages", []):
        if msg.get("role") == "assistant" and "cost_metrics" in msg:
            # Assign different values based on index
            msg["cost_metrics"]["estimated_cost"] = costs[i % len(costs)]
            msg["cost_metrics"]["latency"] = latencies[i % len(latencies)]
            
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

print("Costs updated!")
