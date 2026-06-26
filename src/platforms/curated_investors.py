import time
import json
import logging
from typing import Optional

log = logging.getLogger(__name__)

class CuratedInvestorsScraper:
    def __init__(self, browser, memory):
        self.browser = browser
        self.memory = memory
        self.targets = [
            "https://www.seedtable.com/investors",
            "https://rootdata.com/Investors",
            "https://cryptorank.io/funds"
        ]
        
    def scrape_and_parse(self, llm_parser):
        for target in self.targets:
            log.info(f"Navigating to curated VC list: {target}")
            try:
                # 1. Scrape raw DOM text
                self.browser.driver.get(target)
                time.sleep(5)  # Let it load
                
                # Scroll down a bit to trigger lazy loads if any
                for _ in range(3):
                    self.browser.driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)
                    
                body_text = self.browser.driver.execute_script("return document.body.innerText;")
                
                # 2. Chunk text if it's too massive (LLMs have limits)
                # For simplicity, we just pass the first ~30k characters 
                # (You would typically paginate or chunk this properly)
                chunk = body_text[:30000] 
                
                # 3. LLM Parsing
                prompt = (
                    "Extract all investor leads, VCs, family offices, and business owners from the following text. "
                    "Return ONLY a JSON array of objects. Do not wrap it in markdown. Each object must have these exact keys: "
                    "'name' (string), 'email' (string), 'role' (string), 'fund_name' (string), 'profile_url' (string). "
                    "If an email is not present, skip that lead entirely. We only want leads with emails or extreme high-value contacts."
                )
                
                log.info("Sending scraped data to LLM Brain for extraction...")
                json_str = llm_parser.parse_with_llm(chunk, prompt, llm_choice="chatgpt")
                
                if json_str:
                    self._save_leads(json_str, target)
                    
            except Exception as e:
                log.error(f"Failed to scrape {target}: {e}")

    def _save_leads(self, json_str: str, source_url: str):
        # The LLM might wrap the JSON in markdown code blocks, strip them
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        try:
            leads = json.loads(json_str)
            if not isinstance(leads, list):
                log.warning("LLM did not return a JSON array.")
                return
                
            saved = 0
            for lead in leads:
                email = lead.get("email", "")
                name = lead.get("name", "")
                
                if not email and not name:
                    continue
                    
                # Use the target domain as platform
                platform = source_url.split("/")[2] 
                
                success = self.memory.add_investor_lead(
                    platform=platform,
                    username=name.lower().replace(" ", ""),
                    email=email,
                    name=name,
                    role=lead.get("role", "Investor"),
                    fund_name=lead.get("fund_name", ""),
                    profile_url=lead.get("profile_url", "")
                )
                if success:
                    saved += 1
                    
            log.info(f"Successfully saved {saved} new unique leads from {platform}!")
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to decode LLM JSON: {e}\nRaw output: {json_str}")
