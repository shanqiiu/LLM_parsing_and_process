#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用示例脚本
演示如何使用操作序列拆分工具
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from operation_sequence_splitter import OperationSequenceSplitter
from operation_sequence_splitter.llm_client import MockLLMClient, create_llm_client
import json


def example_basic_usage():
    """示例1: 基本使用"""
    print("="*80)
    print("示例1: 基本使用")
    print("="*80)
    
    # 初始化拆分器（使用Mock客户端，无需API密钥）
    splitter = OperationSequenceSplitter(
        knowledge_base_path="data/manual.example.json",
        llm_client=MockLLMClient()
    )
    
    # 拆分操作序列
    operation = "登录系统并查看用户信息"
    result = splitter.split(operation, output_format="text")
    
    print(f"\n输入: {operation}")
    print(f"\n输出:\n{result}\n")


def example_json_output():
    """示例2: JSON格式输出"""
    print("="*80)
    print("示例2: JSON格式输出")
    print("="*80)
    
    splitter = OperationSequenceSplitter(
        knowledge_base_path="data/manual.example.json",
        llm_client=MockLLMClient()
    )
    
    operation = "创建新任务并设置提醒"
    result_json = splitter.split(operation, output_format="json")
    
    print(f"\n输入: {operation}")
    print(f"\n输出 (JSON):")
    print(result_json)
    
    # 解析JSON
    result_dict = json.loads(result_json)
    print(f"\n解析后: 共 {result_dict['total_steps']} 个子步骤\n")


def example_knowledge_base_query():
    """示例3: 查询知识库"""
    print("="*80)
    print("示例3: 查询知识库信息")
    print("="*80)
    
    splitter = OperationSequenceSplitter(
        knowledge_base_path="data/manual.example.json",
        llm_client=MockLLMClient()
    )
    
    # 获取特定操作的信息
    op_info = splitter.get_operation_info("登录系统")
    if op_info:
        print(f"\n操作: {op_info['name']}")
        print("标准步骤:")
        for i, step in enumerate(op_info['steps'], 1):
            print(f"  {i}. {step}")
    
    # 搜索相关操作
    print("\n搜索'任务'相关操作:")
    results = splitter.knowledge_base.search_related_operations("任务")
    for r in results:
        print(f"  - {r.get('name', 'Unknown')}")
    
    # 获取所有操作
    print("\n所有可用操作:")
    all_ops = splitter.knowledge_base.get_all_operations()
    for op in all_ops:
        print(f"  - {op}")
    
    print()


def example_batch_processing():
    """示例4: 批量处理"""
    print("="*80)
    print("示例4: 批量处理")
    print("="*80)
    
    splitter = OperationSequenceSplitter(
        knowledge_base_path="data/manual.example.json",
        llm_client=MockLLMClient()
    )
    
    operations = [
        "登录系统",
        "创建新任务",
        "发送邮件"
    ]
    
    print(f"\n批量处理 {len(operations)} 个操作序列:\n")
    results = splitter.split_batch(operations, output_format="text")
    
    for i, (op, result) in enumerate(zip(operations, results), 1):
        print(f"{'='*80}")
        print(f"操作 {i}: {op}")
        print(f"{'='*80}")
        print(result)
        print()


def example_with_real_llm():
    """示例5: 使用真实LLM（需要API密钥）"""
    print("="*80)
    print("示例5: 使用真实LLM")
    print("="*80)
    print("\n注意: 此示例需要配置API密钥")
    print("可以通过环境变量或配置文件设置\n")
    
    # 示例：使用OpenAI（需要设置 OPENAI_API_KEY 环境变量）
    # splitter = OperationSequenceSplitter(
    #     knowledge_base_path="data/manual.example.json",
    #     llm_config={
    #         "type": "openai",
    #         "model": "gpt-3.5-turbo"
    #     }
    # )
    # 
    # result = splitter.split("登录系统并查看用户信息")
    # print(result)
    
    print("取消注释上面的代码并设置API密钥后即可使用真实LLM\n")


def main():
    """运行所有示例"""
    print("\n操作序列拆分工具 - 使用示例\n")
    
    examples = [
        example_basic_usage,
        example_json_output,
        example_knowledge_base_query,
        example_batch_processing,
        example_with_real_llm
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ 示例执行失败: {e}\n")
    
    print("="*80)
    print("所有示例执行完成！")
    print("="*80)


if __name__ == "__main__":
    main()

