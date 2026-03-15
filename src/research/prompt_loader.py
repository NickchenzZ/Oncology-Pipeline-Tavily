"""Prompt loading utilities"""

import re
from pathlib import Path
from typing import Dict, List, Optional


SKILL_DIR = Path(__file__).parent.parent.parent
PROMPTS_DIR = SKILL_DIR / "prompts"


def load_prompt(prompt_name: str, **kwargs) -> str:
    """Load a prompt template from the prompts directory"""
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    content = prompt_file.read_text(encoding='utf-8')

    # Replace placeholders
    for key, value in kwargs.items():
        content = content.replace(f"{{{key}}}", str(value))

    return content


def parse_search_section(content: str, section_name: str) -> Optional[Dict]:
    """Parse a search strategy section from markdown content"""
    # Find the section
    pattern = rf"## {section_name}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    section_content = match.group(1)

    # Extract fields
    result = {}

    # Name
    name_match = re.search(r'\*\*名称：\*\*(.*?)(?=\n|\*\*)', section_content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Query
    query_match = re.search(r'\*\*查询：\*\*(.*?)(?=\n\*\*|\Z)', section_content, re.DOTALL)
    if query_match:
        result['query'] = query_match.group(1).strip()

    # Focus
    focus_match = re.search(r'\*\*重点：\*\*(.*?)(?=\n\*\*|\Z)', section_content, re.DOTALL)
    if focus_match:
        result['focus'] = focus_match.group(1).strip()

    return result


def load_search_query(section: str, drug_name: str) -> Dict:
    """Load a search query from search_prompt.md"""
    prompt_file = PROMPTS_DIR / "search_prompt.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Search prompt file not found: {prompt_file}")

    content = prompt_file.read_text(encoding='utf-8')

    result = parse_search_section(content, section)

    if not result:
        raise ValueError(f"Section '{section}' not found in search_prompt.md")

    # Replace drug_name placeholder
    if 'query' in result:
        result['query'] = result['query'].replace('{drug_name}', drug_name)

    return result


def get_all_search_rounds(drug_name: str) -> List[Dict]:
    """Get all search rounds for fast research mode"""
    rounds = []
    for i in range(1, 7):
        try:
            round_config = load_search_query(f'ROUND_{i}', drug_name)
            rounds.append(round_config)
        except Exception as e:
            print(f"[WARN] Failed to load ROUND_{i}: {e}")

    return rounds
