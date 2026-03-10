"""io_handler.py - CSV input/output control"""
from __future__ import annotations
import csv, logging
from pathlib import Path
from .breach_checker import BreachResult

logger = logging.getLogger(__name__)

INPUT_COLUMN = "email"
OUTPUT_COLUMNS = ["email_address", "breached", "site_where_breached"]

def read_email_csv(filepath) -> list[str]:
    """Read email addresses from email_list.csv"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    emails = []
    headers = {"email", "email_address", "e-mail", "emailaddress"}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row.")
        col = None
        for field in reader.fieldnames:
            if field.strip().lower() in headers:
                col = field; break
        if col is None:
            col = reader.fieldnames[0]
            logger.warning("No email column found; using first column %r.", col)
            for row in reader:
                value = row.get(col, "").strip()
                if value:
                    emails.append(value)
    logger.info("Loaded %d email(s) from %s", len(emails), path)
    return emails

def write_results_csv(results: list[BreachResult], filepath) -> None:
    """Write Breach-screening results to a CSV file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_row())
    logger.info("Results written to %s (%d rows)", path, len(results))