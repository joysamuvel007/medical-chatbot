from urllib.parse import urlparse
from typing import List

from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from duckduckgo_search import DDGS

from utils.models import SearchResult
from utils.logger import logger
from config.settings import MAX_SEARCH_RESULTS, TRUSTED_MEDICAL_DOMAINS


# ─── LangChain @tool decorator ────────────────────────────
# This registers the function as a LangChain Tool with:
#   - tool.name         = "medical_web_search"
#   - tool.description  = the docstring (used by LLM to decide when to call it)
#   - tool.args_schema  = inferred from type hints
@tool
def medical_web_search(query: str) -> str:
    """
    Search the web for current medical information using DuckDuckGo.
    Returns a formatted string of results from trusted medical sources.
    Use this when the user asks about specific medical conditions,
    medications, symptoms, or health topics that need current information.
    """
    results = _run_search(query, MAX_SEARCH_RESULTS)
    if not results:
        return "No relevant medical information found."

    lines = []
    for i, r in enumerate(results, 1):
        trust = "✓ Trusted" if r.is_trusted else "Source"
        lines.append(f"[{i}] {r.title} ({trust})\n{r.snippet}\nURL: {r.url}")

    return "\n\n".join(lines)


def _is_trusted(url: str) -> bool:
    """Check if URL belongs to a trusted medical domain."""
    try:
        domain = urlparse(url).netloc.lower().replace("www.", "")
        return any(domain.endswith(d) for d in TRUSTED_MEDICAL_DOMAINS)
    except Exception:
        return False


def _clean_snippet(snippet: str) -> str:
    import re
    clean = re.sub(r'<[^>]+>', '', snippet or '')
    return ' '.join(clean.split())[:300]


def _run_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> List[SearchResult]:
    """
    Core search logic — framework-agnostic.
    Called by both the @tool function and as_runnable().
    """
    logger.info(f"Web search: '{query}'")
    results = []

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(keywords=query, max_results=max_results + 3))
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return []

    for item in raw:
        url = item.get("href", "")
        results.append(SearchResult(
            title=item.get("title", "No title"),
            url=url,
            snippet=_clean_snippet(item.get("body", "")),
            is_trusted=_is_trusted(url),
        ))

    results.sort(key=lambda r: 0 if r.is_trusted else 1)
    final = results[:max_results]

    trusted_count = sum(1 for r in final if r.is_trusted)
    logger.info(f"Search: {len(final)} results ({trusted_count} trusted)")

    return final


class WebSearchAgent:
    """
    Wraps the medical_web_search tool as a class with as_runnable().
    """

    def search(self, query: str, max_results: int = MAX_SEARCH_RESULTS) -> List[SearchResult]:
        """Direct call (used by pipeline.py)."""
        return _run_search(query, max_results)

    def as_runnable(self) -> RunnableLambda:
        """
        Return this agent as a LangChain Runnable.
        Input:  str  (search query)
        Output: List[SearchResult]
        """
        return RunnableLambda(_run_search)

    @property
    def tool(self):
        """
        Expose the @tool-decorated function directly, e.g. for
        binding to a ChatOllama LLM:
            llm_with_tools = llm.bind_tools([web_search_agent.tool])
        """
        return medical_web_search


# ─── Singleton ────────────────────────────────────────────
web_search_agent = WebSearchAgent()
web_search_runnable = web_search_agent.as_runnable()