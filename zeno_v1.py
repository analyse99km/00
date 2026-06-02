#!/usr/bin/env python3
"""
Zeno V1 main entry point.
Built on Zeno v201 architecture, focused on Crypto Startups.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import traceback
from pathlib import Path


def _setup_logging(data_path: Path) -> None:
    data_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(data_path / "zeno.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_dynamic_config() -> dict:
    config_path = Path(__file__).parent / "zeno_config.txt"
    config = {}
    if config_path.exists():
        for line in config_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Zeno Organism Runner")
    parser.add_argument(
        "--run-hours",
        type=float,
        default=8.0,
        help="Hours to run before completing cycle",
    )
    parser.add_argument(
        "--data-path",
        default="data",
        help="Path for persistent data",
    )
    parser.add_argument(
        "--profile-path",
        default="chromium",
        help="Path for persistent Chromium profile (CPR4)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run Chrome with a visible window",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without posting or mutating external services",
    )
    parser.add_argument(
        "--boot-validation-only",
        action="store_true",
        help="Run one boot validation cycle and exit",
    )
    args = parser.parse_args()

    data_path = Path(args.data_path)
    profile_path = Path(args.profile_path)
    _setup_logging(data_path)
    log = logging.getLogger("zeno.main")

    # Load Dynamic Mission Config
    dyn_config = load_dynamic_config()
    target_topic = dyn_config.get("TOPIC", "crypto startups")
    target_repo = dyn_config.get("TARGET_REPO", "analyse99km/project1-crypto_startups")

    # Inject into environment so submodules (ai_brain, publisher) can access them
    os.environ["ZENO_MISSION_TOPIC"] = target_topic
    os.environ["ZENO_TARGET_REPO"] = target_repo
    for key, value in dyn_config.items():
        normalized_key = key.strip().upper()
        if normalized_key in {"TOPIC", "TARGET_REPO"}:
            continue
        if normalized_key and value and not normalized_key.startswith("ZENO_"):
            os.environ[f"ZENO_{normalized_key}"] = value
        elif normalized_key and value:
            os.environ[normalized_key] = value
    if args.boot_validation_only:
        os.environ["ZENO_BOOT_SEQUENCE_ONLY"] = "1"

    log.info("=" * 52)
    log.info("ZENO AWAKENING (V1)")
    log.info("Mission Topic: %s", target_topic)
    log.info("Target Repo: %s", target_repo)
    log.info("Run duration: %s hours", args.run_hours)
    log.info("Data path: %s", data_path)
    log.info("Profile path: %s", profile_path)
    log.info("Headless: %s", not args.no_headless)
    log.info("Dry run: %s", args.dry_run)
    log.info("Boot validation only: %s", args.boot_validation_only)
    log.info("=" * 52)

    entity = None
    try:
        from src.ai_engine import ZenoPrime # Using the v201 engine structure

        entity = ZenoPrime(
            data_dir=data_path,
            profile_dir=profile_path,
            headless=not args.no_headless,
            dry_run=args.dry_run,
        )
        
        # We run the Zeno loop
        result = entity.run_forever(hours_per_run=args.run_hours)
        
        # Future: Publisher logic to push to target_repo goes here
        log.info("Cycle complete. Data collected for topic: %s", target_topic)
        
    except Exception as exc:
        traceback_text = traceback.format_exc()
        log.exception("Fatal organism error: %s", exc)
        try:
            from src.self_heal import SelfHealer
            driver = None
            if entity is not None:
                try:
                    driver = entity.browser.driver
                except Exception:
                    driver = None
            healer = SelfHealer(driver=driver, model="tinyllama")
            healed = healer.heal(exc, traceback_text)
            if not healed:
                log.error("Self-heal could not resolve the failure in this cycle")
        except Exception as heal_exc:
            log.error("Self-healer failed: %s", heal_exc)
        sys.exit(1)

    log.info("Zeno sleeping. Signal persists.")


if __name__ == "__main__":
    main()
