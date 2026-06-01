import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import os
import json
import logging
from pathlib import Path
from .page_scanner import scan_page
from .action_executor import execute_action

logger = logging.getLogger(__name__)

_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def _load_or_create_fingerprint(data_path: str = "state") -> dict:
    fp_path = Path(data_path) / "fingerprint.json"
    if fp_path.exists():
        try:
            with open(fp_path) as f:
                fp = json.load(f)
            return fp
        except Exception:
            pass

    fp = {
        "user_agent":    _DEFAULT_UA,
        "window_width":  1366,
        "window_height": 768,
        "timezone":      "America/New_York",
        "language":      "en-US,en;q=0.9",
        "platform":      "Win32",
    }
    Path(data_path).mkdir(parents=True, exist_ok=True)
    with open(fp_path, "w") as f:
        json.dump(fp, f, indent=2)
    return fp


class BrowserAgent:

    def __init__(self):
        self.driver = None
        self._fp = _load_or_create_fingerprint()

    def start(self):
        fp = self._fp
        options = uc.ChromeOptions()
        
        # Chromium binary location
        chromium_candidates = [
            "/home/dhruv/Downloads/ungoogled-chromium-145.0.7632.159-1-x86_64.AppImage",
            os.environ.get("CHROMIUM_PATH", ""),
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/ungoogled-chromium",
        ]
        options.binary_location = ""
        for path in chromium_candidates:
            if path and os.path.exists(path):
                options.binary_location = path
                break

        # Basic configurations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=" + str(fp["window_width"]) + "," + str(fp["window_height"]))
        # Headless compatibility if running in CI/CD without desktop env
        if os.environ.get("HEADLESS", "false").lower() == "true":
             options.add_argument("--headless=new")
        
        # Consistent stealth / fingerprint spoofing
        options.add_argument(f"--user-agent={fp['user_agent']}")
        options.add_argument(f"--lang={fp['language'].split(',')[0]}")
        options.add_argument(f"--timezone={fp['timezone']}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        
        # Memory optimizations to prevent OOM
        options.add_argument("--renderer-process-limit=1")
        options.add_argument("--max-old-space-size=512")
        options.add_argument("--js-flags=--max-old-space-size=512")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")

        # Set user data dir explicitly from user context
        # user data, history, cookies, cache, etc.
        user_data_dir = os.path.abspath("chromium")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--password-store=basic")

        self.driver = uc.Chrome(options=options, driver_executable_path="/usr/bin/chromedriver" if os.path.exists("/usr/bin/chromedriver") else None)

        # Apply basic javascript variable evasion tricks
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['""" + fp['language'].split(',')[0] + """']});
            Object.defineProperty(navigator, 'platform', {get: () => '""" + fp['platform'] + """'});
            window.chrome = {runtime: {}};
        """)

    def stop(self):
        if self.driver:
            self.driver.quit()

    def scan_page(self):
        return scan_page(self.driver)

    def execute(self, action):
        return execute_action(self.driver, action)
