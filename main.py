#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
操作序列拆分主程序
"""

import argparse
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from operation_sequence_splitter import OperationSequenceSplitter
from operation_sequence_splitter.config import Config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="根据用户操作手册将粗粒度操作序列拆分为细粒度子步骤",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置拆分单个操作序列
  python main.py -i "登录系统并查看用户信息"
  
  # 从文件读取操作序列并输出JSON格式
  python main.py -i input.txt -o output.json -f json
  
  # 使用自定义配置文件
  python main.py -i "操作序列" -c config.json
  
  # 批量处理
  python main.py -i input.txt -b
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入：操作序列文本或包含操作序列的文件路径"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径（可选，如果不指定则输出到控制台）"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式（默认: text）"
    )
    
    parser.add_argument(
        "-k", "--knowledge-base",
        help="操作手册JSON文件路径（覆盖配置文件中的设置）"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="批量处理模式（输入文件每行一个操作序列）"
    )
    
    parser.add_argument(
        "--llm-type",
        choices=["openai", "anthropic", "local", "mock"],
        help="LLM类型（覆盖配置文件）"
    )
    
    parser.add_argument(
        "--llm-model",
        help="LLM模型名称（覆盖配置文件）"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = Config(args.config)
    
    # 确定知识库路径
    kb_path = args.knowledge_base or config.get("knowledge_base.path")
    if not kb_path or not Path(kb_path).exists():
        print(f"❌ 错误: 知识库文件不存在: {kb_path}")
        print("请使用 -k 参数指定有效的操作手册JSON文件路径")
        sys.exit(1)
    
    # 构建LLM配置
    llm_config = config.get_llm_config()
    if args.llm_type:
        llm_config["type"] = args.llm_type
    if args.llm_model:
        llm_config["model"] = args.llm_model
    
    # 初始化拆分器
    try:
        splitter = OperationSequenceSplitter(
            knowledge_base_path=kb_path,
            llm_config=llm_config
        )
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    
    # 读取输入
    input_path = Path(args.input)
    if input_path.exists():
        with open(input_path, 'r', encoding='utf-8') as f:
            if args.batch:
                operation_sequences = [line.strip() for line in f if line.strip()]
            else:
                operation_sequences = [f.read().strip()]
    else:
        # 输入是文本
        operation_sequences = [args.input]
    
    # 执行拆分
    try:
        if len(operation_sequences) == 1:
            result = splitter.split(
                operation_sequences[0],
                output_format=args.format,
                include_context=config.get("output.include_context", True)
            )
            results = [result]
        else:
            results = splitter.split_batch(operation_sequences, output_format=args.format)
    except Exception as e:
        print(f"❌ 拆分失败: {e}")
        sys.exit(1)
    
    # 输出结果
    output_text = "\n\n" + "="*80 + "\n\n".join(results) if len(results) > 1 else results[0]
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"✓ 结果已保存到: {output_path}")
    else:
        print("\n" + "="*80)
        print("拆分结果:")
        print("="*80)
        print(output_text)


if __name__ == "__main__":
    main()

