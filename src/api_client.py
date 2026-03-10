"""api_client.py - Intelligence X API client with retry/backoff."""

from __future__ import annotations
import logging
import time
import uuid
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when the API returns an unrecoverable error."""


class RateLimitError(APIError):
    """Raised on HTTP 429 Too Many Requests."""


class IntelligenceXClient:
    """Client for the Intelligence X free "intelligent" API."""

    SEARCH_ENDPOINT = "/intelligent/search"
    RESULT_ENDPOINT = "/intelligent/search/result"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://free.intelx.io",
        timeout: int = 15,
        request_delay: float = 1.0,
        max_retries: int = 5,
        backoff_factor: float = 2.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(
            {"x-key": self.api_key, "Content-Type": "application/json"}
        )
        return session

    def search_email(self, email: str, correlation_id=None) -> list[str]:
        """Search for breach records for email. Returns list of source names"""
        cid = correlation_id or str(uuid.uuid4())[:8]
        logger.info("[%s] Searching for <%s>", cid, email)
        search_id = self._post_search(email, cid)
        if not search_id:
            logger.warning("[%s] No searchId returned for <%s>", cid, email)
            return []
        time.sleep(self.request_delay)
        results = self._get_results(search_id, cid)
        logger.info("[%s] Found %d result(s) for <%s>", cid, len(results), email)
        return results

    def _post_search(self, term: str, cid: str):
        url = f"{self.base_url}{self.SEARCH_ENDPOINT}"
        payload = {
            "term": term,
            "buckets": [],
            "maxresults": 100,
            "timeout": 0,
            "datefrom": "",
            "dateto": "",
            "sort": 4,
            "media": 0,
            "terminate": [],
        }
        response = self._request("POST", url, json=payload, cid=cid)
        return response.json().get("id") if response else None

    def _get_results(self, search_id: str, cid: str) -> list[str]:
        url = f"{self.base_url}{self.RESULT_ENDPOINT}"
        params = {"id": search_id, "limit": 100, "offset": 0}
        response = self._request("GET", url, params=params, cid=cid)
        if not response:
            return []
        sources = []
        for item in response.json().get("records", []):
            bucket = item.get("bucket", "")
            name = item.get("name", "")
            val = f"{bucket} - {name}" if bucket and name else bucket or name
            if val and val not in sources:
                sources.append(val)
        return sources

    def _request(self, method, url, cid, **kwargs):
        for attempt in range(1, self.max_retries + 2):
            try:
                resp = self._session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                logger.debug(
                    "[%s] %s %s -> HTTP %d (attempt %d)",
                    cid,
                    method,
                    url,
                    resp.status_code,
                    attempt,
                )
                if resp.status_code == 200:
                    return resp
                if resp.status_code == 429:
                    wait = self.backoff_factor**attempt
                    logger.warning("[%s] Rate-limited. Waiting %.1fs.", cid, wait)
                    time.sleep(wait)
                    continue
                if resp.status_code in (401, 403):
                    raise APIError(f"Auth error {resp.status_code} for {url}")
                logger.error("[%s] Unexpected status %d", cid, resp.status_code)
                return None
            except requests.exceptions.Timeout:
                logger.error("[%s] Timeout on attempt %d", cid, attempt)
                time.sleep(self.backoff_factor**attempt)
            except requests.exceptions.ConnectionError as exc:
                logger.error("[%s] Connection error: %s", cid, exc)
                time.sleep(self.backoff_factor**attempt)
        logger.error("[%s] All attempts exhausted for %s", cid, url)
        return None
