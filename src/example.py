"""
example.py - Test of the breach-intelligence API client

Used for:
    *--dry-run mode (no API key, no network calls)
    * Unit testing
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

# Demo breach data
_BREACH_SEED: dict[str, list[str]] = {
    "neil@example.com": ["facebook.com-2025", "serebii.com-2012"]
    , "jane@test.co.uk": ["twitter.com-2028", "instagram.com-2024"]
    , "fiona@company.net": []
    , "william@william.plus.uk": []
    , "joe@example.org": ["tesco.co.uk-2017"]
    , "dee@doug.io": ["dnd3-5.wikidot.com-2026", "foundryvtt.com-2025", "foundryvtt.com-2026", "youtube.com-2015"]
}

class ExampleBreachClient:
    """Simulares the Intelligence X API without connecting to the network."""

    def __init__(self, simulate_error_for: set[str] | None = None) -> None:
        self._errors: set[str] = simulate_error_for or set()
    
    def search_email(self, email:str, correlation_id: str | None = None) -> list[str]:
        """Return example breach sources for emails"""
        cid = correlation_id or "mock"
        if email in self._errors:
            raise RuntimeError(f"Simulated API error for {email}")
        sources = _BREACH_SEED.get(email, [])
        logger.debug("[%s] MockClient: %d source(s) for %s", cid, len(sources), email)
        return list(sources)