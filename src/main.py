"""main.py - CLI entry point for the ALC Breach Screening Tool."""

from __future__ import annotations
import argparse, logging, os, sys
from pathlib import Path
import json
from dotenv import load_dotenv
from .api_client import IntelligenceXClient
from .breach_checker import BreachChecker, SummaryStats
from .io_handler import read_email_csv, write_results_csv
from .example import ExampleBreachClient

load_dotenv()  # Reads .env file

sys.path.insert(0, str(Path(__file__).parent))

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

DEFAULT_CONFIG = {
    "api": {
        "base_url": "https://free.intelx.io",
        "timeout": 15,
        "max_retries": 5,
        "backoff_factor": 2.0,
        "request_delay": 1.0,
    },
    "paths": {"input": "email_list.csv", "output": "output_result.csv"},
    "logging": {"level": "INFO"},
}


def configure_logging(level="INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )


def load_config(config_path):
    cfg = DEFAULT_CONFIG.copy()
    if config_path and Path(config_path).exists():
        with open(config_path) as fh:
            user_cfg = json.load(fh) or {}
        for section, values in user_cfg.items():
            if section in cfg and isinstance(cfg[section], dict):
                cfg[section].update(values)
            else:
                cfg[section] = values
    return cfg


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="ALC Breach Screener")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--dry-run", default="store_true")
    parser.add_argument("--log-level", default=None)
    return parser.parse_args(argv)


def print_summary(stats: SummaryStats):
    print("\n" + "=" * 60)
    print(" ALC BREACH SCREENING - ANALYST SUMMARY")
    print("=" * 60)
    print(f" Total checked  : {stats.total_checked}")
    print(f" Breached       : {stats.total_breached}")
    print(f" Clean          : {stats.total_clean}")
    print(f" Invalid        : {stats.total_invalid}")
    print(f" Breach rate    : {stats.breach_rate:.1f}%")
    if stats.source_counts:
        print("\n Top breach sources:")
        for src, count in stats.top_sources(10):
            print(f"    {count:>4}  {src}")
    print("=" * 60 + "\n")


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = load_config(args.config)
    configure_logging(args.log_level or cfg["logging"].get("level", "INFO"))
    log = logging.getLogger(__name__)
    input_path = Path(args.input or cfg["paths"]["input"])
    output_path = Path(args.output or cfg["paths"]["output"])

    if args.dry_run:
        log.info("DRY-RUN mode: using example data.")
        client = ExampleBreachClient()
    else:
        api_key = os.getenv("IX_API_KEY")
        if not api_key:
            log.error("IX_API_KEY not set. Use --dry-run or set the env var.")
            return 1
        c = cfg["api"]
        client = IntelligenceXClient(
            api_key=api_key,
            base_url=c["base_url"],
            timeout=c["timeout"],
            max_retries=c["max_retries"],
            backoff_factor=c["backoff_factor"],
            request_delay=c["request_delay"],
        )

    try:
        emails = read_email_csv(input_path)
    except (FileNotFoundError, ValueError) as exc:
        log.error("Input error: %s", exc)
        return 1

    if not emails:
        log.warning("No emails to check.")
        return 0

    def progress(idx, total, result):
        status = "BREACHED" if result.breached else "CLEAN  "
        print(f"    [{idx:>3}/{total}] {status} {result.email_address}")

    checker = BreachChecker(
        api_client=client,
        request_delay=cfg["api"]["request_delay"],
        progress_callback=progress,
    )
    try:
        results, stats = checker.check_emails(emails)
    except Exception as exc:
        log.error("Fatal error: %s", exc, exc_info=True)
        return 2

    try:
        write_results_csv(results, output_path)
    except OSError as exc:
        log.errro("Write failed: $s", exc)
        return 2

    print_summary(stats)
    log.info("Output saved to %s", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
