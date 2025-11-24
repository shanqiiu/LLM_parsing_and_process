#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from operation_sequence_splitter import OperationSequenceSplitter
from operation_sequence_splitter.llm_client import MockLLMClient

def test_basic():
    """基本功能测试"""
    print("="*80)
    print("测试1: 基本拆分功能")
    print("="*80)
    
    # 使用示例知识库
    kb_path = "data/manual.example.json"
    if not Path(kb_path).exists():
        print(f"❌ 知识库文件不存在: {kb_path}")
        return False
    
    # 使用Mock客户端进行测试
    splitter = OperationSequenceSplitter(
        knowledge_base_path=kb_path,
        llm_client=MockLLMClient()
    )
    
    # 测试拆分
    operation = "登录系统并查看用户信息"
    print(f"\n输入操作序列: {operation}\n")
    
    result = splitter.split(operation, output_format="text")
    print("拆分结果:")
    print(result)
    print()
    
    return True

def test_json_output():
    """JSON输出格式测试"""
    print("="*80)
    print("测试2: JSON格式输出")
    print("="*80)
    
    kb_path = "data/manual.example.json"
    splitter = OperationSequenceSplitter(
        knowledge_base_path=kb_path,
        llm_client=MockLLMClient()
    )
    
    operation = "创建新任务"
    print(f"\n输入操作序列: {operation}\n")
    
    result = splitter.split(operation, output_format="json")
    print("JSON格式结果:")
    print(result)
    print()
    
    return True

def test_knowledge_base():
    """知识库功能测试"""
    print("="*80)
    print("测试3: 知识库查询功能")
    print("="*80)
    
    kb_path = "data/manual.example.json"
    splitter = OperationSequenceSplitter(
        knowledge_base_path=kb_path,
        llm_client=MockLLMClient()
    )
    
    # 测试获取操作信息
    op_info = splitter.get_operation_info("登录系统")
    if op_info:
        print(f"操作: {op_info['name']}")
        print("步骤:")
        for step in op_info['steps']:
            print(f"  - {step}")
    else:
        print("未找到操作信息")
    
    print()
    
    # 测试搜索
    results = splitter.knowledge_base.search_related_operations("任务")
    print(f"搜索'任务'相关操作: {len(results)} 个结果")
    for r in results:
        print(f"  - {r.get('name', 'Unknown')}")
    
    print()
    
    return True

def main():
    """运行所有测试"""
    print("\n开始测试操作序列拆分工具...\n")
    
    tests = [
        test_basic,
        test_json_output,
        test_knowledge_base
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("✓ 测试通过\n")
            else:
                failed += 1
                print("✗ 测试失败\n")
        except Exception as e:
            failed += 1
            print(f"✗ 测试异常: {e}\n")
    
    print("="*80)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("="*80)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

