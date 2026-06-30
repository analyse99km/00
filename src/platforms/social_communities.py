import time
import json
import logging
import random

log = logging.getLogger(__name__)

class SocialCommunitiesScraper:
    def __init__(self, browser, memory):
        self.browser = browser
        self.memory = memory
        self.targets = [
            "https://discord.com/app",  # Will need specific channel IDs in production
        ]
        
    def _human_jitter(self):
        delay = random.uniform(2.5, 5.0)
        time.sleep(delay)

    def scrape_and_parse(self, llm_parser):
        for target in self.targets:
            log.info(f"Navigating to Social Community: {target}")
            try:
                self.browser.driver.get(target)
                time.sleep(10) # Wait for Discord/App to load the heavy React frontend
                
                # We assume the user has selected a Web3 server and we are ripping the members list.
                # In a real environment, you'd navigate via selenium to specific guilds.
                
                body_text = self.browser.driver.execute_script("return document.body.innerText;")
                chunk = body_text[:35000] 
                
                prompt = (
                    "Extract all high-value members, investors, founders, and VCs from the following Discord/Social text. "
                    "Ignore standard users. We only want Admins, Founders, Investors, or partners. "
                    "Return ONLY a JSON array of objects. Do not wrap it in markdown. Each object must have these exact keys: "
                    "'name' (string), 'email' (string), 'role' (string), 'fund_name' (string), 'profile_url' (string), "
                    "'discord_handle' (string), 'twitter_handle' (string), 'calendly_link' (string)."
                )
                
                log.info("Sending scraped Social data to Hybrid LLM Brain for extraction...")
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
                name = lead.get("name", "")
                discord_handle = lead.get("discord_handle", "")
                
                if not name and not discord_handle:
                    continue
                    
                contact_meta = json.dumps({
                    "discord_handle": discord_handle,
                    "twitter_handle": lead.get("twitter_handle", ""),
                    "calendly_link": lead.get("calendly_link", ""),
                    "email": lead.get("email", "")
                })
                
                success = self.memory.add_investor_lead(
                    platform="discord",
                    username=discord_handle if discord_handle else name.lower().replace(" ", ""),
                    email=lead.get("email", ""),
                    name=name,
                    role=lead.get("role", "Investor/Founder"),
                    fund_name=lead.get("fund_name", ""),
                    profile_url=contact_meta
                )
                if success:
                    saved += 1
                    
            log.info(f"Successfully saved {saved} new unique leads from Discord!")
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to decode LLM JSON: {e}\nRaw output: {json_str}")
