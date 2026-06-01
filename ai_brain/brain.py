from browser.browser_agent import BrowserAgent
from cognition.login_detector import check_login
from cognition.action_planner import decide_action
from cognition.reflector import reflect
from memory.memory_manager import MemoryManager
import time

GOAL = "open x.com and post hello"

def main():

    browser = BrowserAgent()
    memory = MemoryManager()

    browser.start()

    step = 0

    while step < 100:
        print(f"--- Step {step} ---")
        page_state = browser.scan_page()

        if not check_login(browser.driver):
            print("Not logged in")

        action = decide_action(GOAL, page_state)
        print(f"Chosen Action: {action}")

        result = browser.execute(action)
        print(f"Action Result: {result}")

        reflection = reflect(result)
        memory.store(reflection)

        if "goal_complete" in reflection:
            print("Goal completed")
            break

        step += 1
        time.sleep(2)

    browser.stop()

if __name__ == "__main__":
    main()
