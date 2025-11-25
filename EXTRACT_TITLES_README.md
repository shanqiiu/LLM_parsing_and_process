# HTML标题提取工具使用说明

## 功能描述

批量从HTML文件中提取最大标题（h1-h6或title标签），并将文件名和标题保存到JSON文件。

## 安装依赖

```bash
pip install beautifulsoup4 lxml
```

或者安装所有依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 处理指定目录下的HTML文件
python extract_html_titles.py -d /path/to/html/files -o output/titles.json
```

### 递归处理子目录

```bash
# 递归搜索所有子目录中的HTML文件
python extract_html_titles.py -d /path/to/html/files -r -o output/titles.json
```

### 命令行参数

- `-d, --directory`: HTML文件所在目录（必需）
- `-o, --output`: 输出JSON文件路径（必需）
- `-r, --recursive`: 递归搜索子目录（可选）

## 标题提取规则

脚本按以下优先级提取标题：

1. **h1标签** - 最高优先级
2. **h2标签** - 如果没有h1
3. **h3标签** - 如果没有h1和h2
4. **h4标签** - 如果没有h1-h3
5. **h5标签** - 如果没有h1-h4
6. **h6标签** - 如果没有h1-h5
7. **title标签** - 如果没有任何h标签

## 输出格式

生成的JSON文件格式如下：

```json
{
  "total_files": 10,
  "files_with_title": 8,
  "files": [
    {
      "filename": "page1.html",
      "title": "页面标题",
      "full_path": "/full/path/to/page1.html"
    },
    {
      "filename": "page2.html",
      "title": "另一个标题",
      "full_path": "/full/path/to/page2.html"
    },
    {
      "filename": "page3.html",
      "title": "",
      "full_path": "/full/path/to/page3.html"
    }
  ]
}
```

### 字段说明

- `total_files`: 处理的文件总数
- `files_with_title`: 成功提取到标题的文件数
- `files`: 文件列表
  - `filename`: 相对路径文件名
  - `title`: 提取的标题（如果未找到则为空字符串）
  - `full_path`: 文件的完整路径

## 使用示例

### 示例1: 处理当前目录

```bash
python extract_html_titles.py -d . -o titles.json
```

### 示例2: 处理指定目录并递归

```bash
python extract_html_titles.py -d ./html_docs -r -o output/titles.json
```

### 示例3: 处理大量HTML文件

```bash
python extract_html_titles.py -d /data/html_files -r -o /data/titles.json
```

## 输出示例

运行脚本时的输出：

```
找到 10 个HTML文件，开始处理...
✓ [1/10] index.html: 欢迎页面...
✓ [2/10] about.html: 关于我们...
✓ [3/10] contact.html: 联系我们...
⚠ [4/10] empty.html: 未找到标题
✓ [5/10] products.html: 产品列表...
...

处理完成: 成功 9 个, 失败/无标题 1 个
✓ 结果已保存到: output/titles.json

统计信息:
  - 总文件数: 10
  - 有标题的文件: 9
  - 无标题的文件: 1
```

## 错误处理

- 如果文件无法读取，会在结果中记录错误信息
- 如果文件没有标题，`title`字段为空字符串
- 如果目录不存在，会显示错误并退出
- 如果目录中没有HTML文件，会显示警告

## 注意事项

1. **编码问题**: 脚本使用UTF-8编码读取文件，如果遇到编码错误会忽略
2. **文件格式**: 支持`.html`和`.htm`扩展名
3. **性能**: 对于大量文件，处理可能需要一些时间
4. **内存**: 每个HTML文件会完全加载到内存中解析

## Python API使用

也可以作为模块导入使用：

```python
from extract_html_titles import extract_max_title, process_html_files, save_to_json

# 提取单个HTML的标题
html_content = "<html><body><h1>标题</h1></body></html>"
title = extract_max_title(html_content)
print(title)  # 输出: 标题

# 批量处理文件
results = process_html_files("./html_files", recursive=True)

# 保存结果
save_to_json(results, "output/titles.json")
```

## 测试

运行测试脚本验证功能：

```bash
python test_extract_titles.py
```

测试包括：
- 标题提取功能测试
- 批量处理测试
- JSON保存测试

