"""
知识库模块：加载和管理用户操作手册JSON文件
支持从目录加载多个JSON文件，每个文件代表一个操作序列（新格式）
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class KnowledgeBase:
    """操作手册知识库类"""
    
    def __init__(self, json_path: str):
        """
        初始化知识库
        
        Args:
            json_path: 包含JSON文件的目录路径
        """
        self.json_path = Path(json_path)
        if not self.json_path.exists():
            raise FileNotFoundError(f"知识库路径不存在: {json_path}")
        
        if not self.json_path.is_dir():
            raise ValueError(f"知识库路径必须是目录: {json_path}")
        
        # 存储所有操作数据
        self.operations: Dict[str, Dict[str, Any]] = {}  # {operation_id: operation_data}
        self.operations_by_name: Dict[str, str] = {}  # {operation_name: operation_id}
        
        self.load()
    
    def load(self) -> None:
        """从目录加载所有JSON文件"""
        json_files = list(self.json_path.glob("*.json"))
        
        if not json_files:
            raise ValueError(f"目录中没有找到JSON文件: {self.json_path}")
        
        loaded_count = 0
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    operation_data = json.load(f)
                
                # 验证JSON格式
                if not isinstance(operation_data, dict):
                    print(f"⚠ 警告: {json_file.name} 格式不正确，跳过")
                    continue
                
                # 验证新格式：必须包含def字段
                if "def" not in operation_data or not isinstance(operation_data.get("def"), dict):
                    print(f"⚠ 警告: {json_file.name} 不是新格式（缺少def字段），跳过")
                    continue
                
                def_data = operation_data.get("def", {})
                operation_id = def_data.get("id") or operation_data.get("id") or json_file.stem
                operation_name = def_data.get("operation") or operation_data.get("operation") or operation_id
                
                if not operation_id:
                    operation_id = json_file.stem
                if not operation_name:
                    operation_name = operation_id
                
                # 存储完整数据，包括文件名
                operation_data["_filename"] = json_file.name
                operation_data["_filepath"] = str(json_file)
                
                # 存储操作数据
                self.operations[operation_id] = operation_data
                self.operations_by_name[operation_name] = operation_id
                
                loaded_count += 1
                
            except json.JSONDecodeError as e:
                print(f"⚠ 警告: {json_file.name} JSON格式错误: {e}，跳过")
            except Exception as e:
                print(f"⚠ 警告: 加载 {json_file.name} 失败: {e}，跳过")
        
        if loaded_count == 0:
            raise RuntimeError(f"未能加载任何有效的JSON文件")
        
        print(f"✓ 成功加载知识库: {loaded_count} 个操作从目录 {self.json_path}")
    
    def get_operation_by_id(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        根据操作ID获取操作信息
        
        Args:
            operation_id: 操作ID
            
        Returns:
            操作信息字典，如果不存在则返回None
        """
        return self.operations.get(operation_id)
    
    def get_operation_by_name(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        根据操作名称获取操作信息
        
        Args:
            operation_name: 操作名称
            
        Returns:
            操作信息字典，如果不存在则返回None
        """
        operation_id = self.operations_by_name.get(operation_name)
        if operation_id:
            return self.operations.get(operation_id)
        return None
    
    def get_operation_steps(self, operation_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        根据操作名称获取详细步骤
        
        Args:
            operation_name: 操作名称或操作ID
            
        Returns:
            操作步骤列表，如果不存在则返回None
        """
        operation = self.get_operation_by_name(operation_name) or self.get_operation_by_id(operation_name)
        if operation and "def" in operation:
            def_data = operation.get("def", {})
            return def_data.get("substep", [])
        return None
    
    def get_current_main_step(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        获取当前主步骤信息
        
        Args:
            operation_name: 操作名称或操作ID
            
        Returns:
            当前主步骤信息，如果不存在则返回None
        """
        operation = self.get_operation_by_name(operation_name) or self.get_operation_by_id(operation_name)
        if operation and "def" in operation:
            def_data = operation.get("def", {})
            return def_data.get("current_main_step")
        return None
    
    def get_operation_info(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        获取完整的操作信息
        
        Args:
            operation_name: 操作名称或操作ID
            
        Returns:
            完整的操作信息字典
        """
        return self.get_operation_by_name(operation_name) or self.get_operation_by_id(operation_name)
    
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
        
        for operation_id, operation_data in self.operations.items():
            if "def" not in operation_data:
                continue
                
            def_data = operation_data.get("def", {})
            operation_name = def_data.get("operation", "")
            context = def_data.get("context", "")
            scene = def_data.get("scene", "")
            
            # 在名称、上下文、场景中搜索
            if (keyword_lower in operation_name.lower() or 
                keyword_lower in context.lower() or 
                keyword_lower in scene.lower()):
                results.append({
                    "operation_id": operation_id,
                    "operation_name": operation_name,
                    "data": operation_data
                })
        
        return results
    
    def get_all_operations(self) -> List[str]:
        """
        获取所有操作名称列表
        
        Returns:
            操作名称列表
        """
        operations = []
        for operation_data in self.operations.values():
            if "def" in operation_data:
                def_data = operation_data.get("def", {})
                operation_name = def_data.get("operation")
                if operation_name:
                    operations.append(operation_name)
        return list(set(operations))
    
    def get_all_operation_ids(self) -> List[str]:
        """
        获取所有操作ID列表
        
        Returns:
            操作ID列表
        """
        return list(self.operations.keys())
    
    def get_context(self, max_length: int = 2000) -> str:
        """
        获取知识库上下文摘要（用于LLM提示）
        
        Args:
            max_length: 最大长度限制
            
        Returns:
            知识库上下文字符串
        """
        context_parts = []
        
        for operation_data in list(self.operations.values())[:10]:  # 限制前10个
            if "def" not in operation_data:
                continue
                
            def_data = operation_data.get("def", {})
            operation_name = def_data.get("operation", "")
            context = def_data.get("context", "")
            substeps = def_data.get("substep", [])
            
            context_item = f"操作: {operation_name}"
            if context:
                context_item += f"\n上下文: {context}"
            
            # 添加步骤预览
            if substeps:
                steps_preview = []
                for step in substeps[:3]:  # 只显示前3个步骤
                    if isinstance(step, dict):
                        step_desc = step.get("description", "")
                        if step_desc:
                            steps_preview.append(f"  - {step_desc}")
                
                if steps_preview:
                    context_item += f"\n步骤预览:\n" + "\n".join(steps_preview)
            
            context_parts.append(context_item)
        
        context = "\n\n".join(context_parts)
        
        # 截断到最大长度
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        return context
    
    def get_operations_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        根据类别获取操作列表
        
        Args:
            category: 操作类别（从def.feature或其他字段中搜索）
            
        Returns:
            该类别下的操作列表
        """
        results = []
        category_lower = category.lower()
        
        for operation_data in self.operations.values():
            if "def" not in operation_data:
                continue
                
            def_data = operation_data.get("def", {})
            feature = def_data.get("feature", "")
            scene = def_data.get("scene", "")
            
            if category_lower in feature.lower() or category_lower in scene.lower():
                results.append(operation_data)
        
        return results
