import json
import os
from pathlib import Path

FILE = "state/skills.json"

def save_skill(name, steps):
    Path(FILE).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(FILE):
        with open(FILE,"w") as f:
            json.dump({}, f)

    with open(FILE) as f:
        data = json.load(f)

    data[name] = steps

    with open(FILE,"w") as f:
        json.dump(data, f, indent=2)
