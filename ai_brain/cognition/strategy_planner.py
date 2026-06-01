import os
import sys
# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.llama_client import ask_llama

def plan_strategy(goal, world_model):
    prompt = f"""
Goal:
{goal}

Known website structure:
{world_model}

Create a step-by-step strategy for the browser agent to accomplish this goal.
Output each step on a new line.
"""
    return ask_llama(prompt)

def decompose(strategy):
    steps = strategy.split("\n")
    return [s for s in steps if s.strip()]
