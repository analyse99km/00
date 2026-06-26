#!/usr/bin/env python3
"""
Zeno Leads main entry point.
Built on Zeno v201 architecture, focused on Investor Lead Generation.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

def _setup_logging(data_path: Path) -> None:
    data_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(data_path / "zeno_leads.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

def parse_credentials(cred_path: str):
    """Parses read4.txt and injects into environment for Zeno engine."""
    p = Path(cred_path)
    if not p.exists():
        logging.warning(f"Credentials file {cred_path} not found.")
        return
        
    lines = p.read_text(encoding="utf-8").splitlines()
    for line in lines:
        line = line.strip()
        if "GitHub username=" in line:
            os.environ["GITHUB_USERNAME"] = line.split("=")[1].strip()
        elif "GitHub fine grade token=" in line:
            os.environ["GH_PAT_FG"] = line.split("=")[1].strip()
        elif "GitHub token(clasic)=" in line:
            os.environ["GH_PAT"] = line.split("=")[1].strip()
        elif "google.com & gemeni.google.com Id=" in line:
            os.environ["GOOGLE_EMAIL"] = line.split("=")[1].strip()
        elif "google.com & gemeni.google.com pass=" in line.lower():
            os.environ["GOOGLE_PASSWORD"] = line.split("=")[1].strip()
        elif "mail.proton.me Id=" in line:
            os.environ["PROTON_USERNAME"] = line.split("=")[1].strip()
        elif "mail.proton.me Pass=" in line:
            os.environ["PROTON_PASSWORD"] = line.split("=")[1].strip()

def main() -> None:
    parser = argparse.ArgumentParser(description="Zeno Investor Lead Generator")
    parser.add_argument("--run-hours", type=float, default=8.0)
    parser.add_argument("--data-path", default="data")
    parser.add_argument("--profile-path", default="chromium")
    parser.add_argument("--credentials", default=r"C:\Users\HP\Desktop\read4.txt")
    parser.add_argument("--no-headless", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data_path = Path(args.data_path)
    profile_path = Path(args.profile_path)
    _setup_logging(data_path)
    log = logging.getLogger("zeno.leads.main")
    
    # Parse provided credentials
    parse_credentials(args.credentials)

    from src.lead_engine import InvestorLeadEngine

    log.info("====================================================")
    log.info("ZENO LEADS AWAKENING")
    log.info("Mission: Investor Lead Generation")
    log.info(f"Run duration: {args.run_hours} hours")
    log.info(f"Data path: {data_path}")
    log.info(f"Profile path: {profile_path}")
    log.info(f"Headless: {not args.no_headless}")
    log.info("====================================================")

    engine = InvestorLeadEngine(
        profile_dir=profile_path,
        data_dir=data_path,
        headless=not args.no_headless,
        dry_run=args.dry_run,
    )
    
    try:
        engine.run_forever(hours_per_run=args.run_hours)
    except KeyboardInterrupt:
        log.info("Manual interrupt received. Shutting down browser...")
        engine.browser.stop()
        engine.memory.close()
    except Exception as e:
        log.error(f"Engine crash: {e}", exc_info=True)
        engine.browser.stop()
        engine.memory.close()
        raise

if __name__ == "__main__":
    main()
