# 知识库格式说明

## 概述

知识库支持两种模式：
1. **目录模式**（推荐）：在指定目录下放置多个JSON文件，每个文件代表一个操作序列
2. **单文件模式**（兼容旧格式）：单个JSON文件包含所有操作信息

## 目录模式（推荐）

### 目录结构

```
knowledge_base/
├── operation_001.json
├── operation_002.json
├── operation_003.json
└── ...
```

### JSON文件格式

每个JSON文件必须包含以下字段：

```json
{
  "operation_id": "operation_001",          // 操作ID（可选，默认使用文件名）
  "operation_name": "登录系统",              // 操作名称（必需）
  "description": "用户登录到系统的标准流程",  // 操作描述（可选）
  "category": "用户认证",                    // 操作类别（可选）
  "steps": [                                // 操作步骤列表（必需）
    {
      "step_number": 1,                     // 步骤编号（可选）
      "action": "打开登录页面",              // 操作动作（必需）
      "description": "在浏览器中访问系统登录页面",  // 步骤描述（可选）
      "parameters": {                       // 操作参数（可选）
        "url": "https://example.com/login"
      }
    },
    {
      "step_number": 2,
      "action": "输入用户名",
      "description": "在用户名输入框中输入用户账号",
      "parameters": {
        "field": "username",
        "required": true
      }
    }
  ],
  "prerequisites": [],                       // 前置条件列表（可选）
  "expected_result": "成功登录系统，进入主页面"  // 预期结果（可选）
}
```

### 字段说明

#### 顶层字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `operation_id` | string | 否 | 操作唯一标识符，如果不提供则使用文件名（不含扩展名） |
| `operation_name` | string | 是 | 操作名称，用于查询和显示 |
| `description` | string | 否 | 操作的详细描述 |
| `category` | string | 否 | 操作类别，用于分类和搜索 |
| `steps` | array | 是 | 操作步骤列表 |
| `prerequisites` | array | 否 | 前置条件列表，列出执行此操作前需要完成的操作 |
| `expected_result` | string | 否 | 操作完成后的预期结果 |

#### 步骤对象字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `step_number` | integer | 否 | 步骤编号，用于排序 |
| `action` | string | 是 | 操作动作，描述要执行的具体操作 |
| `description` | string | 否 | 步骤的详细描述 |
| `parameters` | object | 否 | 操作参数，包含执行该步骤所需的具体参数 |

### 示例

参考 `data/knowledge_base_example/` 目录中的示例文件：
- `operation_001.json`: 登录系统
- `operation_002.json`: 查看用户信息
- `operation_003.json`: 创建新任务

## 单文件模式（兼容旧格式）

### 格式1: 嵌套结构

```json
{
  "operations": {
    "操作名称": {
      "description": "操作描述",
      "steps": ["步骤1", "步骤2", ...]
    }
  }
}
```

### 格式2: 扁平结构

```json
{
  "操作名称": {
    "steps": ["步骤1", "步骤2", ...]
  }
}
```

### 格式3: 列表结构

```json
[
  {
    "name": "操作名称",
    "steps": ["步骤1", "步骤2", ...]
  }
]
```

## 使用方式

### 命令行

```bash
# 使用目录模式
python main.py -i "操作序列" -k data/knowledge_base_example

# 使用单文件模式
python main.py -i "操作序列" -k data/manual.json
```

### Python API

```python
from operation_sequence_splitter import OperationSequenceSplitter

# 目录模式
splitter = OperationSequenceSplitter(
    knowledge_base_path="data/knowledge_base_example",
    llm_config={"type": "openai", "model": "gpt-3.5-turbo"}
)

# 单文件模式
splitter = OperationSequenceSplitter(
    knowledge_base_path="data/manual.json",
    llm_config={"type": "openai", "model": "gpt-3.5-turbo"}
)
```

## 最佳实践

1. **使用目录模式**：当有多个操作序列时，推荐使用目录模式，每个操作一个文件，便于管理和维护
2. **命名规范**：JSON文件名建议使用有意义的名称，如 `operation_001.json` 或 `login_system.json`
3. **操作ID**：如果JSON文件中没有 `operation_id`，系统会自动使用文件名（不含扩展名）作为ID
4. **步骤描述**：为每个步骤提供清晰的 `action` 和 `description`，有助于LLM更好地理解操作
5. **参数信息**：在 `parameters` 中提供详细的参数信息，有助于生成更精确的子步骤

## 注意事项

1. 目录模式下，所有 `.json` 文件都会被加载
2. 如果JSON文件格式错误，会被跳过并显示警告
3. 操作名称必须唯一，如果重复，后面的会覆盖前面的
4. 步骤中的 `step_number` 如果缺失，会按照数组顺序自动编号

