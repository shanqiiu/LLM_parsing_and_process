"""
LLM客户端模块：支持多种大模型API调用
"""

import os
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量获取
            model: 模型名称
            base_url: API基础URL（用于兼容其他OpenAI兼容的API）
        """
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                base_url=base_url or os.getenv("OPENAI_BASE_URL")
            )
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
        
        self.model = model
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的操作步骤拆分助手，能够将粗粒度的操作序列拆分为详细的、可执行的子步骤。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {e}")


class AnthropicClient(LLMClient):
    """Anthropic Claude API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """
        初始化Anthropic客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量获取
            model: 模型名称
        """
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("请安装anthropic库: pip install anthropic")
        
        self.model = model
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="你是一个专业的操作步骤拆分助手，能够将粗粒度的操作序列拆分为详细的、可执行的子步骤。",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API调用失败: {e}")


class LocalLLMClient(LLMClient):
    """本地LLM客户端（支持Ollama等）"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        初始化本地LLM客户端
        
        Args:
            base_url: 本地LLM服务地址
            model: 模型名称
        """
        import requests
        self.base_url = base_url
        self.model = model
        self.requests = requests
    
    def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"你是一个专业的操作步骤拆分助手。\n\n{prompt}",
                    "stream": False,
                    "options": {"temperature": temperature}
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"本地LLM API调用失败: {e}")


class MockLLMClient(LLMClient):
    """模拟LLM客户端（用于测试）"""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成模拟文本"""
        # 简单的模拟逻辑：将输入的操作拆分为几个子步骤
        lines = prompt.split("\n")
        operation_line = [l for l in lines if "操作序列" in l or "操作" in l]
        
        if operation_line:
            op_text = operation_line[0]
            # 简单的拆分逻辑
            return f"""根据操作手册，我将该操作拆分为以下子步骤：

1. 准备阶段：检查前置条件
2. 执行阶段：{op_text.split('：')[-1] if '：' in op_text else op_text}
3. 验证阶段：确认操作完成
4. 清理阶段：整理相关资源

每个子步骤都是agent可以直接执行的原子操作。"""
        
        return "无法解析操作序列，请提供更详细的信息。"


def create_llm_client(client_type: str = "openai", **kwargs) -> LLMClient:
    """
    创建LLM客户端工厂函数
    
    Args:
        client_type: 客户端类型 ("openai", "anthropic", "local", "mock")
        **kwargs: 客户端初始化参数
        
    Returns:
        LLM客户端实例
    """
    client_type = client_type.lower()
    
    if client_type == "openai":
        return OpenAIClient(**kwargs)
    elif client_type == "anthropic":
        return AnthropicClient(**kwargs)
    elif client_type == "local":
        return LocalLLMClient(**kwargs)
    elif client_type == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"不支持的客户端类型: {client_type}")

