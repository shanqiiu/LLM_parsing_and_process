# 快速开始指南

## 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 设置API密钥（如使用OpenAI）
export OPENAI_API_KEY="your-api-key"
```

## 2. 准备操作手册

将你的操作手册保存为JSON格式，参考 `data/manual.example.json`：

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

## 3. 基本使用

### 命令行方式

```bash
# 基本使用（使用Mock客户端，无需API密钥）
python main.py -i "登录系统并查看用户信息" -k data/manual.example.json --llm-type mock

# 使用真实LLM（需要API密钥）
python main.py -i "创建新任务" -k data/manual.json -f json -o output.json
```

### Python API方式

```python
from operation_sequence_splitter import OperationSequenceSplitter

# 初始化
splitter = OperationSequenceSplitter(
    knowledge_base_path="data/manual.json",
    llm_config={"type": "openai", "model": "gpt-3.5-turbo"}
)

# 拆分操作序列
result = splitter.split("登录系统并查看用户信息")
print(result)
```

## 4. 运行测试

```bash
python test_splitter.py
```

## 5. 查看示例

```bash
python example_usage.py
```

## 常见问题

**Q: 如何切换不同的LLM？**

A: 使用 `--llm-type` 参数或在配置文件中设置：
- `openai`: OpenAI GPT模型
- `anthropic`: Anthropic Claude模型
- `local`: 本地LLM（如Ollama）
- `mock`: Mock客户端（仅测试用）

**Q: 如何自定义输出格式？**

A: 使用 `-f` 参数：
- `text`: 文本格式（默认）
- `json`: JSON格式

**Q: 如何批量处理？**

A: 创建输入文件，每行一个操作序列，然后使用 `-b` 参数：
```bash
python main.py -i input.txt -b -o output.txt
```

