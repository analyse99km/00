import json
import os
from pathlib import Path

FILE = "state/world_model.json"

class WorldModel:
    def __init__(self):
        Path(FILE).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(FILE):
            with open(FILE,"w") as f:
                json.dump({},f)

        with open(FILE) as f:
            self.data = json.load(f)

    def update(self, site, page, page_state):
        if site not in self.data:
            self.data[site] = {"pages":{}}

        self.data[site]["pages"][page] = page_state

        with open(FILE,"w") as f:
            json.dump(self.data,f,indent=2)
            
    def get_model(self):
        return self.data
