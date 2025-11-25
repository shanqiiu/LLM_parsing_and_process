#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试HTML标题提取功能
"""

import os
import tempfile
import json
from pathlib import Path
from extract_html_titles import extract_max_title, process_html_files, save_to_json


def create_test_html_files(test_dir: Path):
    """创建测试用的HTML文件"""
    # 测试文件1：有h1标签
    html1 = """<!DOCTYPE html>
<html>
<head>
    <title>页面标题</title>
</head>
<body>
    <h1>这是最大的标题</h1>
    <h2>这是二级标题</h2>
    <p>内容</p>
</body>
</html>"""
    
    # 测试文件2：只有h2标签
    html2 = """<!DOCTYPE html>
<html>
<head>
    <title>另一个页面</title>
</head>
<body>
    <h2>二级标题</h2>
    <p>内容</p>
</body>
</html>"""
    
    # 测试文件3：只有title标签
    html3 = """<!DOCTYPE html>
<html>
<head>
    <title>只有Title标签的页面</title>
</head>
<body>
    <p>没有标题标签的内容</p>
</body>
</html>"""
    
    # 测试文件4：没有标题
    html4 = """<!DOCTYPE html>
<html>
<body>
    <p>没有任何标题的内容</p>
</body>
</html>"""
    
    (test_dir / "test1.html").write_text(html1, encoding='utf-8')
    (test_dir / "test2.html").write_text(html2, encoding='utf-8')
    (test_dir / "test3.html").write_text(html3, encoding='utf-8')
    (test_dir / "test4.html").write_text(html4, encoding='utf-8')
    
    print(f"✓ 创建了4个测试HTML文件在: {test_dir}")


def test_extract_max_title():
    """测试标题提取函数"""
    print("="*80)
    print("测试1: 提取最大标题")
    print("="*80)
    
    # 测试h1
    html1 = "<html><body><h1>主标题</h1><h2>副标题</h2></body></html>"
    title1 = extract_max_title(html1)
    assert title1 == "主标题", f"期望'主标题'，得到'{title1}'"
    print(f"✓ h1标题提取: {title1}")
    
    # 测试h2（没有h1时）
    html2 = "<html><body><h2>二级标题</h2></body></html>"
    title2 = extract_max_title(html2)
    assert title2 == "二级标题", f"期望'二级标题'，得到'{title2}'"
    print(f"✓ h2标题提取: {title2}")
    
    # 测试只有title标签
    html3 = "<html><head><title>页面标题</title></head><body><p>内容</p></body></html>"
    title3 = extract_max_title(html3)
    assert title3 == "页面标题", f"期望'页面标题'，得到'{title3}'"
    print(f"✓ title标签提取: {title3}")
    
    # 测试无标题
    html4 = "<html><body><p>没有标题</p></body></html>"
    title4 = extract_max_title(html4)
    assert title4 is None, f"期望None，得到'{title4}'"
    print(f"✓ 无标题处理: {title4}")
    
    print("\n✓ 所有测试通过\n")


def test_process_files():
    """测试批量处理文件"""
    print("="*80)
    print("测试2: 批量处理HTML文件")
    print("="*80)
    
    # 创建临时目录和测试文件
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_html_files(test_dir)
        
        # 处理文件
        results = process_html_files(str(test_dir), recursive=False)
        
        # 验证结果
        assert len(results) == 4, f"期望4个文件，得到{len(results)}个"
        
        # 检查结果
        titles = {r["filename"]: r["title"] for r in results}
        assert titles["test1.html"] == "这是最大的标题"
        assert titles["test2.html"] == "二级标题"
        assert titles["test3.html"] == "只有Title标签的页面"
        assert titles["test4.html"] == ""  # 无标题
        
        print(f"✓ 处理了 {len(results)} 个文件")
        for r in results:
            print(f"  - {r['filename']}: {r['title'] or '(无标题)'}")
        
        print("\n✓ 批量处理测试通过\n")


def test_save_json():
    """测试保存JSON"""
    print("="*80)
    print("测试3: 保存JSON文件")
    print("="*80)
    
    test_results = [
        {"filename": "test1.html", "title": "标题1", "full_path": "/path/test1.html"},
        {"filename": "test2.html", "title": "标题2", "full_path": "/path/test2.html"}
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.json"
        save_to_json(test_results, str(output_path))
        
        # 验证文件存在
        assert output_path.exists(), "JSON文件未创建"
        
        # 验证内容
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["total_files"] == 2
        assert data["files_with_title"] == 2
        assert len(data["files"]) == 2
        
        print(f"✓ JSON文件已保存: {output_path}")
        print(f"  - 总文件数: {data['total_files']}")
        print(f"  - 有标题的文件: {data['files_with_title']}")
        
        print("\n✓ JSON保存测试通过\n")


def main():
    """运行所有测试"""
    print("\n开始测试HTML标题提取功能...\n")
    
    try:
        test_extract_max_title()
        test_process_files()
        test_save_json()
        
        print("="*80)
        print("✓ 所有测试通过！")
        print("="*80)
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

