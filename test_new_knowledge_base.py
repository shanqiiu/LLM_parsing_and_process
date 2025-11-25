#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新的知识库格式（目录模式）
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from operation_sequence_splitter import OperationSequenceSplitter
from operation_sequence_splitter.llm_client import MockLLMClient


def test_directory_knowledge_base():
    """测试目录模式的知识库"""
    print("="*80)
    print("测试: 目录模式知识库")
    print("="*80)
    
    # 使用目录路径
    kb_path = "data/knowledge_base_example"
    if not Path(kb_path).exists():
        print(f"❌ 知识库目录不存在: {kb_path}")
        return False
    
    # 初始化拆分器
    splitter = OperationSequenceSplitter(
        knowledge_base_path=kb_path,
        llm_client=MockLLMClient()
    )
    
    # 测试获取所有操作
    print("\n1. 获取所有操作:")
    all_ops = splitter.knowledge_base.get_all_operations()
    for op in all_ops:
        print(f"   - {op}")
    
    # 测试获取所有操作ID
    print("\n2. 获取所有操作ID:")
    all_ids = splitter.knowledge_base.get_all_operation_ids()
    for op_id in all_ids:
        print(f"   - {op_id}")
    
    # 测试按名称获取操作信息
    print("\n3. 按名称获取操作信息:")
    op_info = splitter.get_operation_info("登录系统")
    if op_info:
        print(f"   操作名称: {op_info.get('operation_name')}")
        print(f"   操作ID: {op_info.get('operation_id')}")
        print(f"   类别: {op_info.get('category', 'N/A')}")
        print(f"   描述: {op_info.get('description', 'N/A')}")
        print(f"   步骤数: {len(op_info.get('steps', []))}")
    
    # 测试搜索功能
    print("\n4. 搜索'任务'相关操作:")
    results = splitter.knowledge_base.search_related_operations("任务")
    for r in results:
        print(f"   - {r.get('operation_name', r.get('name', 'Unknown'))}")
    
    # 测试按类别获取操作
    print("\n5. 按类别获取操作:")
    user_ops = splitter.knowledge_base.get_operations_by_category("用户")
    for op in user_ops:
        print(f"   - {op.get('operation_name')} ({op.get('category')})")
    
    # 测试拆分功能
    print("\n6. 测试拆分功能:")
    operation = "登录系统并查看用户信息"
    print(f"   输入: {operation}")
    result = splitter.split(operation, output_format="text")
    print(f"   输出: {result[:200]}...")  # 只显示前200字符
    
    print("\n✓ 测试通过")
    return True


def test_backward_compatibility():
    """测试向后兼容性（单个JSON文件）"""
    print("\n" + "="*80)
    print("测试: 向后兼容性（单个JSON文件）")
    print("="*80)
    
    # 使用单个JSON文件
    kb_path = "data/manual.example.json"
    if not Path(kb_path).exists():
        print(f"⚠ 跳过: 旧格式文件不存在: {kb_path}")
        return True
    
    try:
        splitter = OperationSequenceSplitter(
            knowledge_base_path=kb_path,
            llm_client=MockLLMClient()
        )
        
        # 测试获取操作
        all_ops = splitter.knowledge_base.get_all_operations()
        print(f"\n从旧格式加载了 {len(all_ops)} 个操作:")
        for op in all_ops:
            print(f"   - {op}")
        
        print("\n✓ 向后兼容性测试通过")
        return True
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n开始测试新的知识库格式...\n")
    
    tests = [
        test_directory_knowledge_base,
        test_backward_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"❌ 测试异常: {e}\n")
    
    print("\n" + "="*80)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

