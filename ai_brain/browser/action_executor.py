import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def _h_type(element, text: str):
    """Type like a human."""
    try:
        element.clear()
    except Exception:
        pass
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(0.04, 0.12))

def execute_action(driver, action):
    if not action or "type" not in action:
        return "invalid_action"

    action_type = action["type"].upper()

    try:
        if action_type == "CLICK_BUTTON":
            buttons = driver.find_elements("css selector","button")
            btn = buttons[action["id"]]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(random.uniform(0.5, 1.5))
            btn.click()
            return "clicked"

        elif action_type == "CLICK_LINK":
            links = driver.find_elements("css selector","a")
            link = links[action["id"]]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
            time.sleep(random.uniform(0.5, 1.5))
            link.click()
            return "clicked_link"

        elif action_type == "FILL":
            inputs = driver.find_elements("css selector","input")
            field = inputs[action["id"]]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
            time.sleep(random.uniform(0.5, 1.0))
            _h_type(field, action.get("value", ""))
            return "filled"

        elif action_type == "NAVIGATE":
            driver.get(action["value"])
            time.sleep(random.uniform(1.0, 3.0))
            return "navigated"
            
        elif action_type == "SCROLL":
            amt = random.randint(150, 600)
            driver.execute_script(f"window.scrollBy(0, {amt});")
            time.sleep(random.uniform(0.8, 2.5))
            return "scrolled"
            
        elif action_type == "WAIT":
            time.sleep(random.uniform(2.0, 5.0))
            return "waited"

    except Exception as e:
        return f"error: {str(e)}"
        
    return "no_action"
