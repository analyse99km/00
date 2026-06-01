import time
import random
from selenium.webdriver.common.action_chains import ActionChains

def extract_latest_response(driver):
    messages = driver.find_elements("css selector",".message")
    if not messages:
        return ""
    return messages[-1].text
