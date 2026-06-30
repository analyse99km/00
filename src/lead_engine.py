import time
import logging
import os
from .ai_engine import ZenoPrime
from .platforms.curated_investors import CuratedInvestorsScraper
from .platforms.high_friction_investors import HighFrictionScraper
from .platforms.social_communities import SocialCommunitiesScraper
from .platforms.osint_dorker import OSINTDorker

log = logging.getLogger("zeno.leads")

class InvestorLeadEngine(ZenoPrime):
    """
    Subclasses ZenoPrime to reuse the exact Autonomous Rebirth logic 
    and session management, but runs the Omni-Platform Investor Scraping 
    modules instead of the Deep Audit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize our custom scrapers
        self.curated_scraper = CuratedInvestorsScraper(self.browser, self.memory)
        self.high_friction_scraper = HighFrictionScraper(self.browser, self.memory)
        self.social_scraper = SocialCommunitiesScraper(self.browser, self.memory)
        self.osint_dorker = OSINTDorker(self.browser, self.memory)

    def run_forever(self, hours_per_run: float = 5.5) -> dict:
        """
        Overrides the main run_forever loop to scrape investors instead of auditing X.com.
        Maintains the 5-hour GitHub Actions timeout safety net.
        """
        run_started_at = time.time()
        effective_hours = min(hours_per_run, 5.0) if os.environ.get("GITHUB_ACTIONS") == "true" else hours_per_run
        
        log.info(f"Starting InvestorLeadEngine iteration {self.iteration} | effective_hours={effective_hours}")
        
        shutdown_margin = 300
        end_at = run_started_at + (effective_hours * 3600) - shutdown_margin
        
        # 1. Start browser and warm up LLM Brain
        self.browser.start()
        
        # Ensure LLMs are logged in (we assume ChatGPT is primarily used via test_llms logic in our LLMParser)
        from .llm_parser import LLMParser
        self.llm_parser = LLMParser(self.browser.driver)

        # 2. Loop through platforms
        while time.time() < end_at:
            log.info("Starting a curated investor scraping cycle...")
            
            # Module 1: Seedtable / RootData / etc.
            try:
                self.curated_scraper.scrape_and_parse(self.llm_parser)
            except Exception as e:
                log.error(f"Error in CuratedInvestorsScraper: {e}")
                
            # Module 2: LinkedIn / Crunchbase / Wellfound
            try:
                self.high_friction_scraper.scrape_and_parse(self.llm_parser)
            except Exception as e:
                log.error(f"Error in HighFrictionScraper: {e}")
                
            # Module 3: Discord Web3 Groups
            try:
                self.social_scraper.scrape_and_parse(self.llm_parser)
            except Exception as e:
                log.error(f"Error in SocialCommunitiesScraper: {e}")
                
            # Module 4: Stealth OSINT Dorking (Fallback)
            try:
                self.osint_dorker.scrape_and_parse(self.llm_parser)
            except Exception as e:
                log.error(f"Error in OSINTDorker: {e}")
                
            # If we finish early or want to sleep between rounds
            time.sleep(60)
            
            # Safety break check
            if time.time() >= end_at:
                log.info("Approaching timeout bound. Breaking loop for rebirth.")
                break
                
        # 3. Autonomous Rebirth
        self.browser.stop()
        self.memory.close()
        
        log.info("Preparing for Autonomous Rebirth...")
        rebirth_data = self.prepare_for_rebirth()
        self._complete_rebirth(rebirth_data)
        
        return {
            "mode": "investor_leads",
            "iteration": self.iteration,
            "current_repo": self.current_repo,
            "next_repo": rebirth_data.get("new_repo_name")
        }
