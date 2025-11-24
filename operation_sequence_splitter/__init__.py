"""
操作序列拆分工具
根据用户操作手册将粗粒度操作序列拆分为细粒度的agent可执行子步骤
"""

__version__ = "1.0.0"

from .splitter import OperationSequenceSplitter
from .knowledge_base import KnowledgeBase
from .llm_client import LLMClient

__all__ = [
    "OperationSequenceSplitter",
    "KnowledgeBase",
    "LLMClient",
]

