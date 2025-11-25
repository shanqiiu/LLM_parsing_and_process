"""
操作序列拆分核心模块
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from .knowledge_base import KnowledgeBase
from .llm_client import LLMClient, create_llm_client


class OperationSequenceSplitter:
    """操作序列拆分器"""
    
    def __init__(
        self,
        knowledge_base_path: str,
        llm_client: Optional[LLMClient] = None,
        llm_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化拆分器
        
        Args:
            knowledge_base_path: 操作手册JSON文件目录路径
            llm_client: LLM客户端实例，如果为None则根据llm_config创建
            llm_config: LLM配置字典，格式: {"type": "openai", "model": "gpt-3.5-turbo", ...}
        """
        # 加载知识库
        self.knowledge_base = KnowledgeBase(knowledge_base_path)
        
        # 初始化LLM客户端
        if llm_client is not None:
            self.llm_client = llm_client
        elif llm_config:
            llm_config_copy = llm_config.copy()
            client_type = llm_config_copy.pop("type", "openai")
            self.llm_client = create_llm_client(client_type, **llm_config_copy)
        else:
            self.llm_client = create_llm_client("mock")
            print("⚠ 警告: 未指定LLM配置，使用Mock客户端（仅用于测试）")
    
    def split_to_new_format(
        self,
        operation_sequence: str,
        output_filename: str = None,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        将操作序列拆分为新格式的JSON
        
        Args:
            operation_sequence: 粗粒度操作序列文本
            output_filename: 输出文件名（如"测试数据1.json"），如果为None则自动生成
            include_context: 是否在提示中包含知识库上下文
            
        Returns:
            新格式的JSON字典
        """
        # 构建提示词
        prompt = self._build_prompt(operation_sequence, include_context)
        
        # 调用LLM生成拆分结果
        text_result = self.llm_client.generate(prompt)
        
        # 解析为新格式JSON
        return self._parse_to_new_format(text_result, operation_sequence, output_filename)
    
    def split_to_new_format_file(
        self,
        operation_sequence: str,
        output_path: str,
        include_context: bool = True
    ) -> str:
        """
        将操作序列拆分并保存为新格式的JSON文件
        
        Args:
            operation_sequence: 粗粒度操作序列文本
            output_path: 输出文件路径
            include_context: 是否在提示中包含知识库上下文
            
        Returns:
            输出文件路径
        """
        # 从输出路径提取文件名
        output_path_obj = Path(output_path)
        output_filename = output_path_obj.name
        
        # 生成新格式JSON
        result_dict = self.split_to_new_format(operation_sequence, output_filename, include_context)
        
        # 确保输出目录存在
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def _build_prompt(self, operation_sequence: str, include_context: bool = True) -> str:
        """
        构建LLM提示词
        
        Args:
            operation_sequence: 操作序列文本
            include_context: 是否包含知识库上下文
            
        Returns:
            完整的提示词
        """
        prompt_parts = []
        
        prompt_parts.append("""你是一个专业的操作步骤拆分助手。你的任务是根据用户操作手册，将粗粒度的操作序列拆分为详细的、agent可以直接执行的子步骤序列。

要求：
1. 每个子步骤应该是原子性的、可独立执行的操作
2. 子步骤之间应该有清晰的逻辑顺序
3. 每个子步骤应该包含具体的操作指令，而不是抽象的描述
4. 子步骤应该足够详细，使得agent能够直接执行
5. 参考操作手册中的标准步骤格式和术语""")
        
        # 添加知识库上下文
        if include_context:
            context = self.knowledge_base.get_context(max_length=1500)
            if context:
                prompt_parts.append(f"\n\n【操作手册参考内容】\n{context}")
        
        # 添加待拆分的操作序列
        prompt_parts.append(f"\n\n【待拆分的操作序列】\n{operation_sequence}")
        
        # 添加输出格式要求
        prompt_parts.append("""
\n\n【输出要求】
请将上述操作序列拆分为详细的子步骤，按照以下格式输出：

步骤1: [具体操作描述]
步骤2: [具体操作描述]
步骤3: [具体操作描述]
...

每个步骤应该：
- 使用明确的动作动词（如：点击、输入、选择、验证等）
- 包含具体的操作对象和参数
- 说明预期的结果或验证条件（如适用）

如果操作序列中包含多个独立的任务，请分别列出每个任务的子步骤。""")
        
        return "\n".join(prompt_parts)
    
    def _parse_to_new_format(
        self, 
        text_result: str, 
        operation_sequence: str = "", 
        output_filename: str = None
    ) -> Dict[str, Any]:
        """
        将文本结果解析为新格式的JSON
        
        Args:
            text_result: LLM返回的文本结果
            operation_sequence: 原始操作序列
            output_filename: 输出文件名（如"测试数据1.json"）
            
        Returns:
            新格式JSON字典
        """
        # 解析步骤
        substeps = []
        lines = text_result.split("\n")
        
        current_description = []
        step_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测步骤开始
            if line.startswith("步骤") or line.startswith("Step") or (line and line[0].isdigit()):
                # 保存上一个步骤
                if current_description:
                    substeps.append({
                        "subtype": "action",
                        "description": " ".join(current_description).strip(),
                        "id": f"step_{step_counter:03d}",
                        "type": "operation"
                    })
                    step_counter += 1
                
                # 解析新步骤
                parts = line.split(":", 1)
                if len(parts) == 2:
                    current_description = [parts[1].strip()]
                else:
                    current_description = [line]
            else:
                # 继续当前步骤的描述
                if current_description:
                    current_description.append(line)
                else:
                    # 如果没有步骤编号，创建新步骤
                    if not substeps:
                        current_description = [line]
        
        # 保存最后一个步骤
        if current_description:
            substeps.append({
                "subtype": "action",
                "description": " ".join(current_description).strip(),
                "id": f"step_{step_counter:03d}",
                "type": "operation"
            })
        
        # 如果没有解析到步骤，创建默认步骤
        if not substeps:
            substeps.append({
                "subtype": "action",
                "description": text_result.strip() or operation_sequence,
                "id": "step_001",
                "type": "operation"
            })
        
        # 生成当前时间戳
        current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # 确定文件名
        if output_filename is None:
            output_filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        elif not output_filename.endswith('.json'):
            output_filename += '.json'
        
        # 构建新格式JSON
        return {
            "chunk_id": f"chunk_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "def": {
                "path": {
                    "textual_path": "",
                    "path_uri": ""
                },
                "substep": substeps,
                "feature": "",
                "product_morphology": "",
                "context": operation_sequence,
                "product_info": {
                    "product_line_name": "",
                    "product_id": "",
                    "product_name": ""
                },
                "current_main_step": {
                    "subtype": "main",
                    "description": operation_sequence or "操作序列",
                    "id": "main_step_001",
                    "type": "main_operation"
                },
                "source": output_filename,
                "id": f"operation_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "corpus_source": "",
                "operation": operation_sequence or "操作序列",
                "scene": ""
            },
            "filename": output_filename,
            "from": "splitter",
            "item_info_id": "",
            "kba_id": "",
            "meta_data": {
                "org_embedding": [],
                "data_filter_map": [],
                "source": output_filename,
                "mtime": current_time
            },
            "text": [],
            "uri": f"file:///{output_filename}"
        }
    
    def get_operation_info(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        获取操作手册中特定操作的详细信息
        
        Args:
            operation_name: 操作名称或操作ID
            
        Returns:
            操作信息字典，如果不存在则返回None
        """
        return self.knowledge_base.get_operation_info(operation_name)
