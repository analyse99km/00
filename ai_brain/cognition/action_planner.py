import os
import sys
# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.llama_client import ask_llama

def decide_action(goal, page_state, world_model=None):
    prompt = f"""
Goal:
{goal}

Page:
{page_state}

World Model Context:
{world_model}

Choose your next action based on the state of the page.
Respond in exactly this format:
TYPE ID VALUE

Types allowed: CLICK_BUTTON, CLICK_LINK, FILL, NAVIGATE, SCROLL, WAIT
ID: Integer index from the page state (if applicable, else 0)
VALUE: Optional string value to fill or URL to navigate to.
"""

    response = ask_llama(prompt)

    parts = response.split(maxsplit=2)
    if not parts:
        return {"type": "WAIT"}

    action_type = parts[0]
    action = {
        "type": action_type,
        "id": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    }

    if len(parts) > 2:
        action["value"] = parts[2]

    return action
