# 操作序列拆分工具

根据用户操作手册将粗粒度的操作序列文本拆分为细粒度的、agent可直接执行的子步骤序列。

## 功能特性

- 📚 **知识库支持**: 基于JSON格式的用户操作手册作为外部知识库
- 🤖 **多LLM支持**: 支持OpenAI、Anthropic Claude、本地LLM（Ollama）等多种大模型
- 📝 **灵活输出**: 支持文本和JSON两种输出格式
- 🔄 **批量处理**: 支持批量处理多个操作序列
- ⚙️ **可配置**: 通过配置文件灵活调整参数

## 项目结构

```
.
├── operation_sequence_splitter/    # 核心模块
│   ├── __init__.py
│   ├── knowledge_base.py          # 知识库管理
│   ├── llm_client.py              # LLM客户端
│   ├── splitter.py                # 拆分核心逻辑
│   └── config.py                  # 配置管理
├── data/                          # 数据目录
│   ├── manual.example.json        # 示例操作手册
│   └── input.example.txt          # 示例输入
├── main.py                        # 主程序入口
├── test_splitter.py              # 测试脚本
├── config.example.json           # 示例配置文件
├── requirements.txt              # 依赖列表
└── README.md                     # 本文档
```

## 安装

1. 克隆或下载项目到本地

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量（如使用OpenAI或Anthropic API）：
```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

## 快速开始

### 1. 准备操作手册JSON文件

操作手册JSON文件应包含操作步骤信息，支持多种格式：

**格式1: 嵌套结构**
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

**格式2: 扁平结构**
```json
{
  "操作名称": {
    "steps": ["步骤1", "步骤2", ...]
  }
}
```

**格式3: 列表结构**
```json
[
  {
    "name": "操作名称",
    "steps": ["步骤1", "步骤2", ...]
  }
]
```

参考 `data/manual.example.json` 查看完整示例。

### 2. 使用命令行工具

**基本用法：**
```bash
python main.py -i "登录系统并查看用户信息" -k data/manual.example.json
```

**指定输出文件：**
```bash
python main.py -i "操作序列文本" -o output.txt -k data/manual.json
```

**JSON格式输出：**
```bash
python main.py -i "操作序列文本" -f json -o output.json -k data/manual.json
```

**批量处理：**
```bash
python main.py -i input.txt -b -o output.txt -k data/manual.json
```

**使用配置文件：**
```bash
python main.py -i "操作序列文本" -c config.json
```

### 3. 使用Python API

```python
from operation_sequence_splitter import OperationSequenceSplitter

# 初始化拆分器
splitter = OperationSequenceSplitter(
    knowledge_base_path="data/manual.json",
    llm_config={
        "type": "openai",
        "model": "gpt-3.5-turbo"
    }
)

# 拆分操作序列
result = splitter.split("登录系统并查看用户信息", output_format="text")
print(result)

# JSON格式输出
result_json = splitter.split("创建新任务", output_format="json")
print(result_json)
```

## 配置说明

### 配置文件格式

创建 `config.json` 文件（参考 `config.example.json`）：

```json
{
  "knowledge_base": {
    "path": "data/manual.json"
  },
  "llm": {
    "type": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "output": {
    "format": "text",
    "include_context": true
  }
}
```

### LLM配置选项

**OpenAI:**
```json
{
  "llm": {
    "type": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-key"  // 或使用环境变量 OPENAI_API_KEY
  }
}
```

**Anthropic Claude:**
```json
{
  "llm": {
    "type": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key": "your-key"  // 或使用环境变量 ANTHROPIC_API_KEY
  }
}
```

**本地LLM (Ollama):**
```json
{
  "llm": {
    "type": "local",
    "base_url": "http://localhost:11434",
    "model": "llama2"
  }
}
```

**Mock (测试用):**
```json
{
  "llm": {
    "type": "mock"
  }
}
```

## 命令行参数

```
-i, --input         输入：操作序列文本或文件路径（必需）
-o, --output        输出文件路径（可选，默认输出到控制台）
-f, --format        输出格式：text 或 json（默认: text）
-k, --knowledge-base 操作手册JSON文件路径
-c, --config        配置文件路径
-b, --batch         批量处理模式（输入文件每行一个操作序列）
--llm-type          LLM类型：openai, anthropic, local, mock
--llm-model         LLM模型名称
```

## 输出格式

### 文本格式

```
步骤1: 打开登录页面
步骤2: 输入用户名
步骤3: 输入密码
步骤4: 点击登录按钮
步骤5: 验证登录成功
步骤6: 导航到用户信息页面
步骤7: 点击用户头像或用户名
步骤8: 查看用户详细信息
步骤9: 验证信息显示正确
```

### JSON格式

```json
{
  "original_sequence": "",
  "sub_steps": [
    {
      "step_number": 1,
      "description": "打开登录页面"
    },
    {
      "step_number": 2,
      "description": "输入用户名"
    },
    ...
  ],
  "total_steps": 9
}
```

## 测试

运行测试脚本：

```bash
python test_splitter.py
```

测试包括：
- 基本拆分功能
- JSON格式输出
- 知识库查询功能

## 示例

### 示例1: 简单拆分

```bash
python main.py -i "登录系统" -k data/manual.example.json --llm-type mock
```

### 示例2: 使用真实LLM

```bash
# 设置环境变量
export OPENAI_API_KEY="your-key"

# 运行
python main.py -i "创建新任务并设置提醒" -k data/manual.json -f json -o result.json
```

### 示例3: 批量处理

创建 `input.txt`:
```
登录系统并查看用户信息
创建新任务并设置提醒
发送邮件给团队成员
```

运行：
```bash
python main.py -i input.txt -b -k data/manual.json -o output.txt
```

## 开发

### 添加新的LLM客户端

1. 在 `operation_sequence_splitter/llm_client.py` 中创建新的客户端类，继承 `LLMClient`
2. 实现 `generate` 方法
3. 在 `create_llm_client` 函数中添加新类型

### 扩展知识库格式

在 `operation_sequence_splitter/knowledge_base.py` 的 `get_operation_steps` 方法中添加新的解析逻辑。

## 注意事项

1. **API密钥安全**: 建议使用环境变量存储API密钥，不要将密钥提交到代码仓库
2. **知识库格式**: 确保操作手册JSON文件格式正确，参考示例文件
3. **LLM选择**: 根据实际需求选择合适的LLM，Mock客户端仅用于测试
4. **输出验证**: 建议对LLM输出结果进行人工验证，确保拆分质量

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

