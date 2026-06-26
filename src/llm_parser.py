import time
import json
import logging
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

log = logging.getLogger(__name__)

class LLMParser:
    """
    Automates web UI for LLMs (ChatGPT, Gemini) to parse unstructured scraped HTML 
    into strictly formatted JSON objects.
    """
    
    def __init__(self, driver):
        self.driver = driver
        
    def _bypass_cloudflare(self):
        for _ in range(10):
            title = (self.driver.title or "").lower()
            if "just a moment" in title or "challenge" in title:
                log.info("Cloudflare detected, waiting...")
                time.sleep(3)
            else:
                break

    def parse_with_llm(self, text: str, prompt: str, llm_choice: str = "chatgpt") -> Optional[str]:
        """
        Passes the scraped text and prompt to the specified LLM via its Web UI.
        Returns the parsed output string.
        """
        # Save current window handle
        main_window = self.driver.current_window_handle
        
        # Open new tab
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        try:
            if llm_choice == "chatgpt":
                return self._ask_chatgpt(text, prompt)
            elif llm_choice == "gemini":
                return self._ask_gemini(text, prompt)
            else:
                log.error(f"Unknown LLM choice: {llm_choice}")
                return None
        finally:
            # Always close the LLM tab and return to main window
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(main_window)

    def _ask_chatgpt(self, text: str, prompt: str) -> Optional[str]:
        url = "https://chatgpt.com/"
        input_css = ["#prompt-textarea", "textarea[data-id='root']", "[role='textbox']"]
        output_css = ["div[data-message-author-role='assistant']", ".markdown"]
        return self._automate_llm(url, input_css, output_css, f"{prompt}\n\n{text}")

    def _ask_gemini(self, text: str, prompt: str) -> Optional[str]:
        url = "https://gemini.google.com/app"
        input_css = ["div[contenteditable='true']", "textarea", "rich-textarea"]
        output_css = ["message-content", ".model-response-text", "[data-response-index]"]
        return self._automate_llm(url, input_css, output_css, f"{prompt}\n\n{text}")

    def _automate_llm(self, url, input_css_list, output_css_list, full_prompt) -> Optional[str]:
        self.driver.get(url)
        time.sleep(8)
        self._bypass_cloudflare()
        
        inp = None
        for css in input_css_list:
            try:
                inp = self.driver.find_element(By.CSS_SELECTOR, css)
                if inp.is_displayed():
                    break
            except:
                continue
                
        if not inp:
            log.error(f"Could not find input element for {url}")
            return None
            
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", inp)
            time.sleep(1)
            inp.click()
        except:
            self.driver.execute_script("arguments[0].click();", inp)
            
        time.sleep(1)
        
        try:
            inp.send_keys(full_prompt)
            time.sleep(0.5)
            inp.send_keys(Keys.RETURN)
        except Exception:
            self.driver.execute_script("arguments[0].value = arguments[1];", inp, full_prompt)
            time.sleep(0.5)
            inp.send_keys(Keys.RETURN)
            
        log.info(f"Sent prompt to LLM. Waiting for response...")
        time.sleep(20) # Wait for LLM to type
        
        resps = []
        for css in output_css_list:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, css)
                if elements and elements[-1].text.strip():
                    resps = elements
                    break
            except:
                pass
                
        if resps:
            return resps[-1].text.strip()
            
        log.warning("Could not extract clean response text, attempting fallback...")
        try:
            all_divs = self.driver.find_elements(By.CSS_SELECTOR, "div, p, article, span")
            longest_text = ""
            for d in all_divs:
                txt = d.text.strip()
                if txt and len(txt) > len(longest_text) and "Extract all investor" not in txt:
                    longest_text = txt
            return longest_text if len(longest_text) > 10 else None
        except Exception as e:
            log.error(f"Fallback extraction failed: {e}")
            return None
