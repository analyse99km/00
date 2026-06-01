import json
import os
from pathlib import Path

FILE = "state/memory.json"

class MemoryManager:

    def __init__(self):
        Path(FILE).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(FILE):
            with open(FILE,"w") as f:
                json.dump([],f)

    def store(self, entry):
        with open(FILE) as f:
            data = json.load(f)

        data.append(entry)

        if len(data) > 50:
            data = data[-50:]

        with open(FILE,"w") as f:
            json.dump(data,f,indent=2)
