"""
操作序列拆分核心模块
"""

import json
from typing import List, Dict, Any, Optional
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
            knowledge_base_path: 操作手册JSON文件路径
            llm_client: LLM客户端实例，如果为None则根据llm_config创建
            llm_config: LLM配置字典，格式: {"type": "openai", "model": "gpt-3.5-turbo", ...}
        """
        # 加载知识库
        self.knowledge_base = KnowledgeBase(knowledge_base_path)
        
        # 初始化LLM客户端
        if llm_client is not None:
            self.llm_client = llm_client
        elif llm_config:
            self.llm_client = create_llm_client(**llm_config)
        else:
            # 默认使用mock客户端
            self.llm_client = create_llm_client("mock")
            print("⚠ 警告: 未指定LLM配置，使用Mock客户端（仅用于测试）")
    
    def split(
        self,
        operation_sequence: str,
        output_format: str = "text",
        include_context: bool = True
    ) -> str:
        """
        将粗粒度操作序列拆分为细粒度子步骤
        
        Args:
            operation_sequence: 粗粒度操作序列文本
            output_format: 输出格式 ("text" 或 "json")
            include_context: 是否在提示中包含知识库上下文
            
        Returns:
            拆分后的子步骤序列（文本或JSON格式）
        """
        # 构建提示词
        prompt = self._build_prompt(operation_sequence, include_context)
        
        # 调用LLM生成拆分结果
        result = self.llm_client.generate(prompt)
        
        # 格式化输出
        if output_format == "json":
            return self._parse_to_json(result)
        else:
            return result
    
    def split_batch(
        self,
        operation_sequences: List[str],
        output_format: str = "text"
    ) -> List[str]:
        """
        批量拆分操作序列
        
        Args:
            operation_sequences: 操作序列列表
            output_format: 输出格式
            
        Returns:
            拆分结果列表
        """
        results = []
        for i, seq in enumerate(operation_sequences, 1):
            print(f"处理第 {i}/{len(operation_sequences)} 个操作序列...")
            result = self.split(seq, output_format)
            results.append(result)
        return results
    
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
        
        # 添加任务描述
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
    
    def _parse_to_json(self, text_result: str) -> str:
        """
        将文本结果解析为JSON格式
        
        Args:
            text_result: LLM返回的文本结果
            
        Returns:
            JSON格式字符串
        """
        steps = []
        lines = text_result.split("\n")
        
        current_step = None
        current_description = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测步骤开始（支持多种格式）
            if line.startswith("步骤") or line.startswith("Step") or line[0].isdigit():
                # 保存上一个步骤
                if current_step is not None:
                    steps.append({
                        "step_number": current_step,
                        "description": " ".join(current_description).strip()
                    })
                
                # 解析新步骤
                parts = line.split(":", 1)
                if len(parts) == 2:
                    step_num_str = parts[0].strip()
                    # 提取步骤编号
                    step_num = "".join(filter(str.isdigit, step_num_str))
                    current_step = int(step_num) if step_num else len(steps) + 1
                    current_description = [parts[1].strip()]
                else:
                    current_step = len(steps) + 1
                    current_description = [line]
            else:
                # 继续当前步骤的描述
                if current_description:
                    current_description.append(line)
                else:
                    # 如果没有步骤编号，创建新步骤
                    if not steps:
                        current_step = 1
                        current_description = [line]
        
        # 保存最后一个步骤
        if current_step is not None:
            steps.append({
                "step_number": current_step,
                "description": " ".join(current_description).strip()
            })
        
        # 如果没有解析到步骤，返回原始文本
        if not steps:
            steps = [{"step_number": 1, "description": text_result}]
        
        result = {
            "original_sequence": "",
            "sub_steps": steps,
            "total_steps": len(steps)
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def get_operation_info(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        获取操作手册中特定操作的详细信息
        
        Args:
            operation_name: 操作名称
            
        Returns:
            操作信息字典，如果不存在则返回None
        """
        steps = self.knowledge_base.get_operation_steps(operation_name)
        if steps:
            return {
                "name": operation_name,
                "steps": steps
            }
        return None

