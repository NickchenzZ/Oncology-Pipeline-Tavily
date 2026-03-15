"""Tavily research executor"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError("tavily-python not installed. Run: pip install tavily-python")

from .prompt_loader import get_all_search_rounds
from ..utils.logger import Logger
from ..utils.retry import retry

# Default configuration
MAX_CONTEXT_CHARS = 30000


@dataclass
class ResearchSource:
    """Represents a research source"""
    title: str
    url: str
    content: str
    score: float = 0.0


class TavilyResearchExecutor:
    """Executes research using Tavily API"""

    def __init__(self, tavily_api_key: Optional[str] = None,
                 verbose: bool = True):
        self.tavily_api_key = tavily_api_key or os.getenv('TAVILY_API_KEY')

        if not self.tavily_api_key:
            raise ValueError("Tavily API key not provided. Set TAVILY_API_KEY environment variable.")

        self.tavily = TavilyClient(api_key=self.tavily_api_key)
        self.logger = Logger(verbose=verbose)
        self.all_sources: List[ResearchSource] = []

    @retry(max_retries=3, delay=1.0, exceptions=(ConnectionError, TimeoutError, OSError))
    async def search(self, query: str, max_results: int = 20,
                     search_depth: str = "advanced") -> Dict[str, Any]:
        """Execute a single search query"""
        self.logger.info(f"Searching: {query[:60]}...")

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.tavily.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=True,
                include_raw_content=True
            )
        )

        return result

    async def execute_research(self, drug_name: str) -> Dict[str, Any]:
        """Execute multi-round research with concurrent searches"""
        self.logger.ok(f"Starting Research (6-Round): {drug_name}")

        # Get all search rounds
        rounds = get_all_search_rounds(drug_name)

        if not rounds:
            raise ValueError("No search rounds configured")

        self.logger.info(f"Search strategy: {len(rounds)} rounds (concurrent)")

        # Execute all rounds concurrently
        async def _search_round(idx: int, round_config: Dict) -> Optional[Dict]:
            self.logger.info(f"[Round {idx}/{len(rounds)}] {round_config.get('name', 'Unknown')}")
            try:
                result = await self.search(
                    round_config['query'],
                    max_results=20,
                    search_depth="advanced"
                )
                return {'idx': idx, 'config': round_config, 'result': result}
            except Exception as e:
                self.logger.warn(f"  Round {idx} failed: {e}")
                return None

        tasks = [_search_round(idx, rc) for idx, rc in enumerate(rounds, 1)]
        completed = await asyncio.gather(*tasks)

        # Deduplicate and collect results in order
        all_sources = []
        seen_urls = set()
        round_summaries = []

        for item in completed:
            if item is None:
                continue
            idx = item['idx']
            round_config = item['config']
            result = item['result']

            round_sources = self._extract_sources(result)
            new_sources = []

            for src in round_sources:
                if src.url not in seen_urls:
                    seen_urls.add(src.url)
                    new_sources.append(src)
                    all_sources.append(src)

            self.logger.ok(f"  [Round {idx}] Found {len(round_sources)} sources, {len(new_sources)} new")

            round_summaries.append({
                'round': idx,
                'name': round_config.get('name', f'Round {idx}'),
                'query': round_config['query'],
                'sources_found': len(round_sources),
                'sources_new': len(new_sources),
                'answer': result.get('answer', '')
            })

        # Sort summaries by round number
        round_summaries.sort(key=lambda x: x['round'])

        self.all_sources = all_sources
        self.logger.ok(f"\nSearch complete: {len(all_sources)} total unique sources")

        # Build context for report generation by caller
        context = self._build_context(all_sources, round_summaries=round_summaries)

        return {
            'drug_name': drug_name,
            'mode': 'research',
            'sources_count': len(all_sources),
            'sources': [{'title': s.title, 'url': s.url, 'content': s.content, 'score': s.score} for s in all_sources],
            'rounds': round_summaries,
            'context': context
        }

    def _extract_sources(self, search_result: Dict[str, Any]) -> List[ResearchSource]:
        """Extract sources from Tavily search result"""
        sources = []

        for result in search_result.get('results', []):
            source = ResearchSource(
                title=result.get('title', 'Untitled'),
                url=result.get('url', ''),
                content=result.get('content', ''),
                score=result.get('score', 0.0)
            )
            sources.append(source)

        return sources

    def _build_context(self, sources: List[ResearchSource],
                       round_summaries: Optional[List] = None) -> str:
        """Build context string from sources with dynamic content budget"""
        context_parts = []

        if round_summaries:
            context_parts.append("=== 多轮搜索结果 ===")
            for rs in round_summaries:
                context_parts.append(f"\n轮次 {rs['round']}: {rs['name']}")
                context_parts.append(f"查询: {rs['query']}")
                context_parts.append(f"来源: {rs['sources_new']} 新 / {rs['sources_found']} 总计")
                if rs.get('answer'):
                    context_parts.append(f"摘要: {rs['answer'][:200]}...")

        # Calculate overhead from metadata
        overhead = sum(len(p) for p in context_parts)
        remaining_budget = MAX_CONTEXT_CHARS - overhead

        # Dynamic content truncation: distribute budget across sources
        capped_sources = sources[:30]
        per_source_budget = max(200, remaining_budget // max(len(capped_sources), 1))

        context_parts.append(f"\n=== 详细来源 ({len(sources)} 个) ===")

        for i, src in enumerate(capped_sources, 1):
            context_parts.append(f"\n[{i}] {src.title}")
            context_parts.append(f"URL: {src.url}")
            truncated = src.content[:per_source_budget]
            if len(src.content) > per_source_budget:
                truncated += "..."
            context_parts.append(f"Content: {truncated}")

        return '\n'.join(context_parts)
