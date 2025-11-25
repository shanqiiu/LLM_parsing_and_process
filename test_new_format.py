#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新格式JSON的加载和生成
"""

import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from operation_sequence_splitter import OperationSequenceSplitter
from operation_sequence_splitter.llm_client import MockLLMClient


def test_load_new_format():
    """测试加载新格式的知识库"""
    print("="*80)
    print("测试1: 加载新格式知识库")
    print("="*80)
    
    kb_path = "data/knowledge_base_new_format"
    if not Path(kb_path).exists():
        print(f"⚠ 跳过: 知识库目录不存在: {kb_path}")
        return True
    
    try:
        splitter = OperationSequenceSplitter(
            knowledge_base_path=kb_path,
            llm_client=MockLLMClient()
        )
        
        # 测试获取操作
        all_ops = splitter.knowledge_base.get_all_operations()
        print(f"\n加载了 {len(all_ops)} 个操作:")
        for op in all_ops:
            print(f"   - {op}")
        
        # 测试获取步骤
        steps = splitter.knowledge_base.get_operation_steps("登录系统")
        if steps:
            print(f"\n操作'登录系统'的步骤数: {len(steps)}")
            for i, step in enumerate(steps[:3], 1):
                if isinstance(step, dict):
                    print(f"   步骤{i}: {step.get('description', step.get('action', ''))}")
        
        # 测试获取主步骤
        main_step = splitter.knowledge_base.get_current_main_step("登录系统")
        if main_step:
            print(f"\n主步骤: {main_step.get('description', 'N/A')}")
        
        print("\n✓ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_new_format():
    """测试生成新格式JSON"""
    print("\n" + "="*80)
    print("测试2: 生成新格式JSON")
    print("="*80)
    
    kb_path = "data/knowledge_base_new_format"
    if not Path(kb_path).exists():
        # 使用旧格式知识库
        kb_path = "data/knowledge_base_example"
    
    try:
        splitter = OperationSequenceSplitter(
            knowledge_base_path=kb_path,
            llm_client=MockLLMClient()
        )
        
        operation = "登录系统并查看用户信息"
        print(f"\n输入: {operation}")
        
        # 生成新格式JSON
        result_dict = splitter.split_to_new_format(operation, "测试数据1.json")
        
        # 验证格式
        assert "chunk_id" in result_dict
        assert "def" in result_dict
        assert "substep" in result_dict["def"]
        assert "current_main_step" in result_dict["def"]
        assert "filename" in result_dict
        assert result_dict["filename"] == "测试数据1.json"
        assert "meta_data" in result_dict
        assert "mtime" in result_dict["meta_data"]
        assert result_dict["def"]["source"] == "测试数据1.json"
        
        print(f"\n生成的JSON结构:")
        print(f"  - chunk_id: {result_dict['chunk_id']}")
        print(f"  - filename: {result_dict['filename']}")
        print(f"  - source: {result_dict['def']['source']}")
        print(f"  - mtime: {result_dict['meta_data']['mtime']}")
        print(f"  - 子步骤数: {len(result_dict['def']['substep'])}")
        print(f"  - 主步骤: {result_dict['def']['current_main_step']['description']}")
        
        # 保存示例文件
        output_path = Path("output/test_output.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 示例文件已保存到: {output_path}")
        
        print("\n✓ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_new_format_file():
    """测试保存新格式JSON文件"""
    print("\n" + "="*80)
    print("测试3: 保存新格式JSON文件")
    print("="*80)
    
    kb_path = "data/knowledge_base_new_format"
    
    try:
        splitter = OperationSequenceSplitter(
            knowledge_base_path=kb_path,
            llm_client=MockLLMClient()
        )
        
        operation = "创建新任务"
        output_path = "output/测试数据1.json"
        
        print(f"\n输入: {operation}")
        print(f"输出路径: {output_path}")
        
        result_path = splitter.split_to_new_format_file(operation, output_path)
        
        # 验证文件存在
        assert Path(result_path).exists()
        
        # 读取并验证内容
        with open(result_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data["filename"] == "测试数据1.json"
        assert saved_data["def"]["source"] == "测试数据1.json"
        assert "mtime" in saved_data["meta_data"]
        
        print(f"\n✓ 文件已保存: {result_path}")
        print(f"  - filename: {saved_data['filename']}")
        print(f"  - source: {saved_data['def']['source']}")
        print(f"  - mtime: {saved_data['meta_data']['mtime']}")
        
        print("\n✓ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n开始测试新格式JSON...\n")
    
    tests = [
        test_load_new_format,
        test_generate_new_format,
        test_save_new_format_file
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

