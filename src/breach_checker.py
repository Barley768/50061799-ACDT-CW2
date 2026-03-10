"""
breach_checker.py - Core logic
"""
from __future__ import annotations
import logging, re, time, uuid
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9._%+\-]+\.[a-zA-Z]{2,}$"
)

@dataclass
class BreachResult:
    """Holds the results for a single email"""
    email_address: str
    breached: bool
    breach_sources: list[str] = field(default_factory=list)

    @property
    def site_where_breached(self) -> str:
        return ";".join(self.breach_sources)
    
    def to_row(self) -> dict[str, str]:
        return{
            "email_address": self.email_address
            , "breached": str(self.breached)
            , "site_where_breached": self.site_where_breached
        }

@dataclass
class SummaryStats:
    """Aggregated analyst summary from a batch of BreachResult objects."""
    total_checked: int=0
    total_breached: int=0
    total_clean: int=0
    total_invalid: int=0
    source_counts: dict[str, int] = field(default_factory=dict)

    @property
    def breach_rate(self) -> float:
        valid = self.total_checked - self.total_invalid
        return (self.total_breached / valid * 100) if valid else 0.0
    
    def top_sources(self, n: int = 10) -> list[tuple[str, int]]:
        return sorted(self.source_counts.items(), key=lambda x: x[1], reverse=True)[:n]
    
def is_valid_email(email: str) -> bool:
    """Return True when email matches a basic RFC-5321 (email) pattern"""
    return bool(EMAIL_RE.match(email.strip()))

class BreachChecker:
    """Runs batch screening of email addresses against Intelligence X API."""
    def __init__(self, api_client, request_delay: float = 1.0, progress_callback = None) -> None:
        self._client = api_client
        self._delay = request_delay
        self._progress = progress_callback
    
    def check_emails(self, emails: list[str]):
        """Check every email address, returns (results, stats)."""
        cleaned = [e.strip() for e in emails if e.strip()]
        total = len(cleaned)
        logger.info("Starting batch check: %d email(s)", total)
        results, stats = [], SummaryStats(total_checked=total)

        for idx, email in enumerate(cleaned, start=1):
            cid = str(uuid.uuid4())[:8]
            if not is_valid_email(email):
                logger.warning("[%s] Invalid email: %r", cid, email)
                result = BreachResult(email, False, ["INVALID_EMAIL"])
                stats.total_invalid += 1
            else:
                result = self._check_single(email, cid)
                if result.breached:
                    stats.total_breached += 1
                    for src in result.breach_sources:
                        stats.source_counts[src] = stats.source_counts.get(src,0)+1
                else:
                    stats.total_clean += 1
            results.append(result)
            if self._progress:
                self._progress(idx, total, result)
            if idx < total:
                time.sleep(self._delay)
        
        logger.info("Batch complete. Breached=%d Clean=%d Invalid=%d", stats.total_breached, stats.total_clean, stats.total_invalid)
        return results, stats
    
    def _check_single(self, email: str, cid:str):
        try:
            sources = self._client.search_email(email, correlation_id=cid)
            return BreachResult(email, bool(sources), sources)
        except Exception as exc:
            logger.error("[%s] Error checking <%s>: %s", cid, email, exc)
            return BreachResult(email, False, ["CHECK_ERROR"])