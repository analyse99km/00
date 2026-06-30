import time
import json
import logging
import random
from typing import Optional

log = logging.getLogger(__name__)

class HighFrictionScraper:
    def __init__(self, browser, memory):
        self.browser = browser
        self.memory = memory
        # Targets that require authenticated scraping via cpr4
        self.targets = [
            "https://www.linkedin.com/search/results/people/?keywords=web3%20investor",
            "https://www.crunchbase.com/discover/contacts",
            "https://wellfound.com/role/investors",
        ]
        
    def _human_jitter(self):
        """Random delay to simulate human reading/clicking and prevent ban"""
        delay = random.uniform(3.5, 8.2)
        log.info(f"Stealth Mode: Waiting for {delay:.2f} seconds...")
        time.sleep(delay)
        
    def _stealth_scroll(self):
        """Scrolls down randomly to mimic human behavior and trigger lazy loading"""
        for _ in range(random.randint(3, 5)):
            scroll_amt = random.randint(300, 800)
            self.browser.driver.execute_script(f"window.scrollBy(0, {scroll_amt});")
            self._human_jitter()

    def scrape_and_parse(self, llm_parser):
        for target in self.targets:
            log.info(f"Navigating to High-Friction target: {target}")
            try:
                self.browser.driver.get(target)
                self._human_jitter()
                
                # Perform stealth scrolling to load all contacts/leads
                self._stealth_scroll()
                    
                body_text = self.browser.driver.execute_script("return document.body.innerText;")
                chunk = body_text[:35000] # Safe LLM context window size
                
                # Aggressive contact extraction prompt based on user request
                prompt = (
                    "Extract all investor leads, VCs, family offices, and business owners from the following text. "
                    "Return ONLY a JSON array of objects. Do not wrap it in markdown. Each object must have these exact keys: "
                    "'name' (string), 'email' (string), 'role' (string), 'fund_name' (string), 'profile_url' (string), "
                    "'linkedin_url' (string), 'twitter_handle' (string), 'calendly_link' (string). "
                    "You MUST extract ALL contact methods you can find (emails, LinkedIn URLs, Twitter handles). "
                    "If a contact method is missing, leave the string empty."
                )
                
                log.info("Sending scraped data to Hybrid LLM Brain for extraction...")
                json_str = llm_parser.parse_with_llm(chunk, prompt, llm_choice="chatgpt")
                
                if json_str:
                    self._save_leads(json_str, target)
                    
            except Exception as e:
                log.error(f"Failed to scrape {target}: {e}")

    def _save_leads(self, json_str: str, source_url: str):
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
                    
                platform = source_url.split("/")[2].replace("www.", "")
                
                # Use metadata field to store all contact methods natively
                contact_meta = json.dumps({
                    "linkedin_url": lead.get("linkedin_url", ""),
                    "twitter_handle": lead.get("twitter_handle", ""),
                    "calendly_link": lead.get("calendly_link", ""),
                    "profile_url": lead.get("profile_url", "")
                })
                
                success = self.memory.add_investor_lead(
                    platform=platform,
                    username=name.lower().replace(" ", ""),
                    email=email,
                    name=name,
                    role=lead.get("role", "Investor"),
                    fund_name=lead.get("fund_name", ""),
                    profile_url=contact_meta  # Hijacking profile_url in schema to store rich contact metadata
                )
                if success:
                    saved += 1
                    
            log.info(f"Successfully saved {saved} new unique leads with contact details from {platform}!")
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to decode LLM JSON: {e}\nRaw output: {json_str}")
