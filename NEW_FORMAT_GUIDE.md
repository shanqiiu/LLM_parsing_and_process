# 新格式JSON使用指南

## 概述

系统现在支持新的JSON格式，每个JSON文件代表一个步骤拆分文件，包含完整的操作序列信息。

## 新格式结构

```json
{
  "chunk_id": "chunk_20251124194222",
  "def": {
    "path": {
      "textual_path": "",
      "path_uri": ""
    },
    "substep": [
      {
        "subtype": "action",
        "description": "操作描述",
        "id": "step_001",
        "type": "operation"
      }
    ],
    "feature": "",
    "product_morphology": "",
    "context": "操作上下文",
    "product_info": {
      "product_line_name": "",
      "product_id": "",
      "product_name": ""
    },
    "current_main_step": {
      "subtype": "main",
      "description": "主操作描述",
      "id": "main_step_001",
      "type": "main_operation"
    },
    "source": "测试数据1.json",
    "id": "operation_20251124194222",
    "corpus_source": "",
    "operation": "操作名称",
    "scene": ""
  },
  "filename": "测试数据1.json",
  "from": "splitter",
  "item_info_id": "",
  "kba_id": "",
  "meta_data": {
    "org_embedding": [],
    "data_filter_map": [],
    "source": "测试数据1.json",
    "mtime": "2025-11-24T19:42:22"
  },
  "text": [],
  "uri": "file:///测试数据1.json"
}
```

## 关键字段说明

### 自动更新的字段

系统会自动更新以下字段：

1. **`def.substep`**: 子步骤列表，包含拆分后的详细步骤
   - `subtype`: 步骤子类型（如"action"）
   - `description`: 步骤描述
   - `id`: 步骤ID（格式：step_001, step_002...）
   - `type`: 步骤类型（如"operation"）

2. **`def.current_main_step`**: 当前主步骤信息
   - `subtype`: "main"
   - `description`: 主操作描述（来自输入的操作序列）
   - `id`: 主步骤ID（格式：main_step_001）
   - `type`: "main_operation"

3. **`def.source`**: 当前生成的文件名称（如"测试数据1.json"）

4. **`meta_data.mtime`**: 当前时间戳（格式：YYYY-MM-DDTHH:MM:SS）

5. **`filename`**: 当前文件名（与source相同）

## 使用方法

### 命令行方式

```bash
# 生成新格式JSON文件
python main.py -i "登录系统并查看用户信息" -k data/knowledge_base_new_format -f new_json -o output/测试数据1.json
```

### Python API方式

```python
from operation_sequence_splitter import OperationSequenceSplitter

# 初始化拆分器
splitter = OperationSequenceSplitter(
    knowledge_base_path="data/knowledge_base_new_format",
    llm_config={"type": "openai", "model": "gpt-3.5-turbo"}
)

# 方法1: 生成新格式JSON字典
result_dict = splitter.split_to_new_format(
    "登录系统并查看用户信息",
    output_filename="测试数据1.json"
)

# 方法2: 直接保存为新格式JSON文件
output_path = splitter.split_to_new_format_file(
    "登录系统并查看用户信息",
    "output/测试数据1.json"
)
```

## 知识库格式

知识库支持两种格式：

### 新格式（推荐）

知识库中的JSON文件使用新格式，包含`def.substep`和`def.current_main_step`字段：

```json
{
  "chunk_id": "chunk_001",
  "def": {
    "substep": [...],
    "current_main_step": {...},
    "operation": "登录系统",
    ...
  },
  ...
}
```

### 旧格式（兼容）

仍然支持旧的格式，系统会自动转换。

## 输出格式对比

### 旧格式（text/json）

```
步骤1: 打开登录页面
步骤2: 输入用户名
...
```

### 新格式（new_json）

```json
{
  "def": {
    "substep": [
      {
        "subtype": "action",
        "description": "打开登录页面",
        "id": "step_001",
        "type": "operation"
      },
      ...
    ],
    "current_main_step": {
      "subtype": "main",
      "description": "登录系统",
      "id": "main_step_001",
      "type": "main_operation"
    },
    "source": "测试数据1.json"
  },
  "filename": "测试数据1.json",
  "meta_data": {
    "mtime": "2025-11-24T19:42:22"
  }
}
```

## 注意事项

1. **文件名**: `filename`和`def.source`字段会自动设置为指定的输出文件名
2. **时间戳**: `meta_data.mtime`会自动设置为当前时间
3. **步骤ID**: 子步骤ID自动生成（step_001, step_002...）
4. **主步骤**: `current_main_step`的描述来自输入的操作序列文本
5. **上下文**: `def.context`字段会包含原始操作序列文本

## 示例

参考以下文件：
- `data/knowledge_base_new_format/example_001.json`: 新格式知识库示例
- `output/test_output.json`: 生成的新格式JSON示例
- `test_new_format.py`: 测试脚本示例

