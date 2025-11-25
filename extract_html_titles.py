#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量提取HTML文件的最大标题
从指定目录下的所有HTML文件中提取最大标题（h1或最大的标题标签），
并将文件名和标题保存到JSON文件
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


def extract_max_title(html_content: str) -> Optional[str]:
    """
    从HTML内容中提取最大标题
    
    Args:
        html_content: HTML内容字符串
        
    Returns:
        最大标题文本，如果未找到则返回None
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 按优先级查找标题：h1 > h2 > h3 > h4 > h5 > h6
        for tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            title_tag = soup.find(tag_name)
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                if title_text:
                    return title_text
        
        # 如果没有找到标题标签，尝试查找title标签
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if title_text:
                return title_text
        
        return None
    except Exception as e:
        print(f"⚠ 解析HTML时出错: {e}")
        return None


def process_html_files(directory: str, recursive: bool = False) -> List[Dict[str, str]]:
    """
    批量处理HTML文件，提取标题
    
    Args:
        directory: HTML文件所在目录
        recursive: 是否递归搜索子目录
        
    Returns:
        包含文件名和标题的字典列表
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    if not directory_path.is_dir():
        raise ValueError(f"路径不是目录: {directory}")
    
    # 查找所有HTML文件
    if recursive:
        html_files = list(directory_path.rglob("*.html")) + list(directory_path.rglob("*.htm"))
    else:
        html_files = list(directory_path.glob("*.html")) + list(directory_path.glob("*.htm"))
    
    if not html_files:
        print(f"⚠ 警告: 在目录 {directory} 中未找到HTML文件")
        return []
    
    results = []
    processed_count = 0
    failed_count = 0
    
    print(f"找到 {len(html_files)} 个HTML文件，开始处理...")
    
    for html_file in html_files:
        try:
            # 读取HTML文件
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # 提取标题
            title = extract_max_title(html_content)
            
            if title:
                # 使用相对路径作为文件名
                relative_path = html_file.relative_to(directory_path)
                results.append({
                    "filename": str(relative_path),
                    "title": title,
                    "full_path": str(html_file)
                })
                processed_count += 1
                print(f"✓ [{processed_count}/{len(html_files)}] {relative_path}: {title[:50]}...")
            else:
                failed_count += 1
                relative_path = html_file.relative_to(directory_path)
                print(f"⚠ [{processed_count + failed_count}/{len(html_files)}] {relative_path}: 未找到标题")
                results.append({
                    "filename": str(relative_path),
                    "title": "",
                    "full_path": str(html_file)
                })
        
        except Exception as e:
            failed_count += 1
            relative_path = html_file.relative_to(directory_path) if html_file.is_relative_to(directory_path) else html_file.name
            print(f"❌ 处理 {relative_path} 时出错: {e}")
            results.append({
                "filename": str(relative_path),
                "title": "",
                "full_path": str(html_file),
                "error": str(e)
            })
    
    print(f"\n处理完成: 成功 {processed_count} 个, 失败/无标题 {failed_count} 个")
    return results


def save_to_json(results: List[Dict[str, str]], output_path: str) -> None:
    """
    将结果保存到JSON文件
    
    Args:
        results: 结果列表
        output_path: 输出JSON文件路径
    """
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        "total_files": len(results),
        "files_with_title": len([r for r in results if r.get("title")]),
        "files": results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 结果已保存到: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="批量提取HTML文件的最大标题并保存到JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理当前目录下的HTML文件
  python extract_html_titles.py -d . -o titles.json
  
  # 递归处理子目录
  python extract_html_titles.py -d ./html_files -r -o titles.json
  
  # 处理指定目录并保存
  python extract_html_titles.py -d /path/to/html -o output/titles.json
        """
    )
    
    parser.add_argument(
        "-d", "--directory",
        required=True,
        help="HTML文件所在目录"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="输出JSON文件路径"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="递归搜索子目录"
    )
    
    args = parser.parse_args()
    
    try:
        # 处理HTML文件
        results = process_html_files(args.directory, args.recursive)
        
        if not results:
            print("❌ 没有找到任何HTML文件或无法提取标题")
            return
        
        # 保存到JSON
        save_to_json(results, args.output)
        
        # 统计信息
        files_with_title = len([r for r in results if r.get("title")])
        print(f"\n统计信息:")
        print(f"  - 总文件数: {len(results)}")
        print(f"  - 有标题的文件: {files_with_title}")
        print(f"  - 无标题的文件: {len(results) - files_with_title}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

