import os
from pathlib import Path

def save_response(name, text):
    dir_path = "storage/responses"
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    with open(f"{dir_path}/{name}.txt", "w", encoding="utf-8") as f:
        f.write(text)

def read_response(name):
    path = f"storage/responses/{name}.txt"
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
