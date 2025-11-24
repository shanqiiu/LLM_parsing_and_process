"""
配置文件模块
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
        if config_path and Path(config_path).exists():
            self.load_from_file(config_path)
        else:
            self.load_default()
    
    def load_default(self):
        """加载默认配置"""
        self.config = {
            "knowledge_base": {
                "path": "data/manual.json"
            },
            "llm": {
                "type": "openai",  # openai, anthropic, local, mock
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000,
                "api_key": None,  # 从环境变量获取
                "base_url": None
            },
            "output": {
                "format": "text",  # text, json
                "include_context": True
            },
            "logging": {
                "level": "INFO",
                "file": None
            }
        }
    
    def load_from_file(self, config_path: str):
        """从文件加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"⚠ 警告: 加载配置文件失败: {e}，使用默认配置")
            self.load_default()
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键，如 "llm.model"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        llm_config = self.get("llm", {}).copy()
        
        # 从环境变量获取API密钥
        if not llm_config.get("api_key"):
            llm_type = llm_config.get("type", "openai")
            if llm_type == "openai":
                llm_config["api_key"] = os.getenv("OPENAI_API_KEY")
            elif llm_type == "anthropic":
                llm_config["api_key"] = os.getenv("ANTHROPIC_API_KEY")
        
        return llm_config

