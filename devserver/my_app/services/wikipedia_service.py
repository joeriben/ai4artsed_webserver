"""
Wikipedia Service: Secure Wikipedia API client for LLM research capability

This service provides the LLM with access to Wikipedia during prompt interception,
allowing it to fetch factual information about cultural heritages, arts, aesthetics,
and other educational contexts.

Security:
- Whitelist-only: Only *.wikipedia.org URLs are accessible
- Language validation: Only allowed language codes accepted
- URL encoding: Search terms properly encoded
- Content truncation: Prevents memory exhaustion

Architecture:
- This is a fundamental capability of ALL interceptions
- NOT a separate pipeline - integrated at chunk execution level
- Language auto-detected from input text (falls back to config default)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from functools import lru_cache
import time
import logging
import re
import urllib.parse
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

# Supported Wikipedia languages (ISO 639-1 codes)
SUPPORTED_LANGUAGES = frozenset([
    'de',  # German
    'en',  # English
    'it',  # Italian
    'fr',  # French
    'es',  # Spanish
    'pt',  # Portuguese
    'nl',  # Dutch
    'pl',  # Polish
    'ru',  # Russian
    'zh',  # Chinese
    'ja',  # Japanese
    'ko',  # Korean
    'ar',  # Arabic
    'tr',  # Turkish
    'hi',  # Hindi
    'sv',  # Swedish
    'uk',  # Ukrainian
    'cs',  # Czech
    'el',  # Greek
    'he',  # Hebrew
])

# Maximum content length per summary (characters)
MAX_CONTENT_LENGTH = 2000

# HTTP timeout for Wikipedia API requests
HTTP_TIMEOUT = 10.0

# User-Agent required by Wikipedia API (https://meta.wikimedia.org/wiki/User-Agent_policy)
HTTP_USER_AGENT = "AI4ArtsEd-DevServer/1.0 (https://github.com/ai4artsed; ai4artsed@example.org) Python/aiohttp"


@dataclass
class WikipediaResult:
    """Result from a Wikipedia lookup"""
    term: str
    language: str
    title: str
    extract: str
    url: str
    success: bool
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"[Wikipedia: {self.title}] {self.extract}"
        return f"[Wikipedia: {self.term}] Not found: {self.error}"


class WikipediaCache:
    """Simple time-based cache for Wikipedia results"""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, tuple] = {}  # key -> (result, timestamp)
        self._ttl = ttl_seconds

    def _make_key(self, term: str, language: str) -> str:
        return f"{language}:{term.lower()}"

    def get(self, term: str, language: str) -> Optional[WikipediaResult]:
        """Get cached result if not expired"""
        key = self._make_key(term, language)
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                logger.debug(f"[WIKI-CACHE] Hit for '{term}' ({language})")
                return result
            else:
                # Expired
                del self._cache[key]
        return None

    def set(self, term: str, language: str, result: WikipediaResult) -> None:
        """Cache a result"""
        key = self._make_key(term, language)
        self._cache[key] = (result, time.time())
        logger.debug(f"[WIKI-CACHE] Stored '{term}' ({language})")

    def clear(self) -> None:
        """Clear all cached results"""
        self._cache.clear()


class WikipediaService:
    """
    Secure Wikipedia API client for LLM research during prompt interception.

    Uses Wikipedia REST API: https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}

    Security constraints:
    - Only queries *.wikipedia.org (whitelist)
    - Only allows known language codes
    - URL-encodes search terms to prevent injection
    - Limits content length to prevent memory exhaustion
    """

    def __init__(self, cache_ttl: int = 3600):
        self._cache = WikipediaCache(ttl_seconds=cache_ttl)

    def _create_session(self) -> aiohttp.ClientSession:
        """Create a new aiohttp session with required headers"""
        timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
        headers = {
            'User-Agent': HTTP_USER_AGENT,
            'Accept': 'application/json'
        }
        return aiohttp.ClientSession(timeout=timeout, headers=headers)

    def _validate_language(self, language: str) -> bool:
        """Check if language code is in whitelist"""
        return language.lower() in SUPPORTED_LANGUAGES

    def _build_url(self, term: str, language: str) -> str:
        """
        Build Wikipedia API URL with proper encoding.

        Security: URL is constructed from whitelist + encoded term only.
        No user-controlled URL components except the search term (encoded).
        """
        # Validate language (whitelist only)
        lang_code = language.lower()
        if lang_code not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

        # URL-encode the search term (prevents injection)
        encoded_term = urllib.parse.quote(term.strip(), safe='')

        # Construct URL from hardcoded template
        url = f"https://{lang_code}.wikipedia.org/api/rest_v1/page/summary/{encoded_term}"

        return url

    async def lookup(self, term: str, language: str = 'de') -> WikipediaResult:
        """
        Look up a term on Wikipedia.

        Args:
            term: Search term (will be URL-encoded)
            language: ISO 639-1 language code (default: 'de')

        Returns:
            WikipediaResult with success=True and extract, or success=False with error
        """
        # Normalize language code
        lang_code = language.lower()

        # Validate language
        if not self._validate_language(lang_code):
            logger.warning(f"[WIKI] Invalid language code '{language}', using 'de'")
            lang_code = 'de'

        # Check cache first
        cached = self._cache.get(term, lang_code)
        if cached:
            return cached

        # Build URL (validates language again)
        try:
            url = self._build_url(term, lang_code)
        except ValueError as e:
            return WikipediaResult(
                term=term,
                language=lang_code,
                title='',
                extract='',
                url='',
                success=False,
                error=str(e)
            )

        logger.info(f"[WIKI] Looking up '{term}' on {lang_code}.wikipedia.org")

        try:
            # Create session per-request to avoid event loop issues
            async with self._create_session() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract summary text
                        extract = data.get('extract', '')
                        title = data.get('title', term)
                        page_url = data.get('content_urls', {}).get('desktop', {}).get('page', url)

                        # Truncate if too long
                        if len(extract) > MAX_CONTENT_LENGTH:
                            extract = extract[:MAX_CONTENT_LENGTH] + '...'

                        result = WikipediaResult(
                            term=term,
                            language=lang_code,
                            title=title,
                            extract=extract,
                            url=page_url,
                            success=True
                        )

                        logger.info(f"[WIKI] Found '{title}': {len(extract)} chars")

                    elif response.status == 404:
                        # Article not found
                        result = WikipediaResult(
                            term=term,
                            language=lang_code,
                            title='',
                            extract='',
                            url='',
                            success=False,
                            error=f"No Wikipedia article found for '{term}'"
                        )
                        logger.info(f"[WIKI] Not found: '{term}'")

                    else:
                        # Other HTTP error
                        result = WikipediaResult(
                            term=term,
                            language=lang_code,
                            title='',
                            extract='',
                            url='',
                            success=False,
                            error=f"Wikipedia API error: HTTP {response.status}"
                        )
                        logger.warning(f"[WIKI] HTTP error {response.status} for '{term}'")

        except asyncio.TimeoutError:
            result = WikipediaResult(
                term=term,
                language=lang_code,
                title='',
                extract='',
                url='',
                success=False,
                error="Wikipedia API timeout"
            )
            logger.warning(f"[WIKI] Timeout for '{term}'")

        except Exception as e:
            result = WikipediaResult(
                term=term,
                language=lang_code,
                title='',
                extract='',
                url='',
                success=False,
                error=f"Wikipedia lookup failed: {str(e)}"
            )
            logger.error(f"[WIKI] Error for '{term}': {e}")

        # Cache result (even failures, to avoid repeated lookups)
        self._cache.set(term, lang_code, result)

        return result

    async def lookup_multiple(
        self,
        terms: List[tuple],  # List of (term, language) tuples
        max_lookups: int = 5
    ) -> List[WikipediaResult]:
        """
        Look up multiple terms concurrently.

        Args:
            terms: List of (term, language) tuples
            max_lookups: Maximum number of lookups (prevents abuse)

        Returns:
            List of WikipediaResults
        """
        # Limit number of lookups
        limited_terms = terms[:max_lookups]
        if len(terms) > max_lookups:
            logger.warning(f"[WIKI] Limited from {len(terms)} to {max_lookups} lookups")

        # Execute lookups concurrently
        tasks = [self.lookup(term, lang) for term, lang in limited_terms]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                term, lang = limited_terms[i]
                final_results.append(WikipediaResult(
                    term=term,
                    language=lang,
                    title='',
                    extract='',
                    url='',
                    success=False,
                    error=str(result)
                ))
            else:
                final_results.append(result)

        return final_results


# Singleton instance (lazy initialization)
_wikipedia_service: Optional[WikipediaService] = None


def get_wikipedia_service(cache_ttl: int = 3600) -> WikipediaService:
    """Get the singleton WikipediaService instance

    Note: Creates new instance each time to avoid event loop issues
    when called from different threads/asyncio contexts.
    """
    # Don't use singleton - aiohttp session is tied to event loop
    # Creating new instance ensures session uses current event loop
    return WikipediaService(cache_ttl=cache_ttl)
