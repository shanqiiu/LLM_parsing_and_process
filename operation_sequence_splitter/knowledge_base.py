"""
知识库模块：加载和管理用户操作手册JSON文件
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class KnowledgeBase:
    """操作手册知识库类"""
    
    def __init__(self, json_path: str):
        """
        初始化知识库
        
        Args:
            json_path: 操作手册JSON文件路径
        """
        self.json_path = Path(json_path)
        if not self.json_path.exists():
            raise FileNotFoundError(f"知识库文件不存在: {json_path}")
        
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """加载JSON知识库文件"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✓ 成功加载知识库: {self.json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载知识库失败: {e}")
    
    def get_operation_steps(self, operation_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        根据操作名称获取详细步骤
        
        Args:
            operation_name: 操作名称
            
        Returns:
            操作步骤列表，如果不存在则返回None
        """
        # 支持多种JSON结构
        if isinstance(self.data, dict):
            # 结构1: {"operations": {"操作名": {"steps": [...]}}}
            if "operations" in self.data:
                ops = self.data["operations"]
                if operation_name in ops:
                    op_data = ops[operation_name]
                    if "steps" in op_data:
                        return op_data["steps"]
                    return op_data if isinstance(op_data, list) else None
            
            # 结构2: {"操作名": {"steps": [...]}}
            if operation_name in self.data:
                op_data = self.data[operation_name]
                if "steps" in op_data:
                    return op_data["steps"]
                return op_data if isinstance(op_data, list) else None
            
            # 结构3: {"操作名": [...]}
            if operation_name in self.data:
                steps = self.data[operation_name]
                return steps if isinstance(steps, list) else None
        
        elif isinstance(self.data, list):
            # 结构4: [{"name": "操作名", "steps": [...]}, ...]
            for item in self.data:
                if isinstance(item, dict):
                    if item.get("name") == operation_name:
                        return item.get("steps", [])
                    if item.get("operation") == operation_name:
                        return item.get("steps", [])
        
        return None
    
    def search_related_operations(self, keyword: str) -> List[Dict[str, Any]]:
        """
        根据关键词搜索相关操作
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的操作列表
        """
        results = []
        keyword_lower = keyword.lower()
        
        if isinstance(self.data, dict):
            if "operations" in self.data:
                ops = self.data["operations"]
                for op_name, op_data in ops.items():
                    if keyword_lower in op_name.lower():
                        results.append({"name": op_name, "data": op_data})
            else:
                for op_name, op_data in self.data.items():
                    if keyword_lower in op_name.lower():
                        results.append({"name": op_name, "data": op_data})
        
        elif isinstance(self.data, list):
            for item in self.data:
                if isinstance(item, dict):
                    op_name = item.get("name") or item.get("operation", "")
                    if keyword_lower in op_name.lower():
                        results.append(item)
        
        return results
    
    def get_all_operations(self) -> List[str]:
        """
        获取所有操作名称列表
        
        Returns:
            操作名称列表
        """
        operations = []
        
        if isinstance(self.data, dict):
            if "operations" in self.data:
                operations = list(self.data["operations"].keys())
            else:
                operations = [k for k in self.data.keys() if isinstance(self.data[k], (dict, list))]
        
        elif isinstance(self.data, list):
            for item in self.data:
                if isinstance(item, dict):
                    op_name = item.get("name") or item.get("operation")
                    if op_name:
                        operations.append(op_name)
        
        return operations
    
    def get_context(self, max_length: int = 2000) -> str:
        """
        获取知识库上下文摘要（用于LLM提示）
        
        Args:
            max_length: 最大长度限制
            
        Returns:
            知识库上下文字符串
        """
        context_parts = []
        
        if isinstance(self.data, dict):
            if "operations" in self.data:
                ops = self.data["operations"]
                for op_name, op_data in ops.items():
                    if "description" in op_data:
                        context_parts.append(f"操作: {op_name}\n描述: {op_data['description']}")
                    elif "steps" in op_data:
                        steps_str = "\n".join([f"  - {s}" if isinstance(s, str) else f"  - {s.get('step', s)}" 
                                             for s in op_data["steps"][:3]])
                        context_parts.append(f"操作: {op_name}\n步骤预览:\n{steps_str}")
            else:
                for op_name, op_data in list(self.data.items())[:10]:
                    if isinstance(op_data, dict) and "description" in op_data:
                        context_parts.append(f"操作: {op_name}\n描述: {op_data['description']}")
        
        context = "\n\n".join(context_parts)
        
        # 截断到最大长度
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        return context

