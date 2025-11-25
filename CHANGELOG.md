# 更新日志

## 2024 - 知识库格式升级

### 新增功能

1. **目录模式知识库支持**
   - 支持从目录加载多个JSON文件
   - 每个JSON文件代表一个操作序列
   - 自动扫描目录下的所有 `.json` 文件

2. **新的JSON文件格式**
   - 更结构化的操作定义
   - 支持操作ID、名称、描述、类别等元数据
   - 详细的步骤定义，包含动作、描述和参数
   - 支持前置条件和预期结果

3. **增强的查询功能**
   - 按操作ID查询
   - 按操作名称查询
   - 按类别查询操作
   - 关键词搜索（支持在名称、描述、类别中搜索）

### 改进

1. **向后兼容性**
   - 保持对旧格式单文件JSON的支持
   - 自动检测是文件还是目录
   - 自动转换旧格式到新格式

2. **错误处理**
   - 更好的错误提示
   - 跳过格式错误的JSON文件并继续处理
   - 详细的加载日志

3. **代码优化**
   - 更清晰的代码结构
   - 更好的类型提示
   - 改进的文档字符串

### 文件变更

- `operation_sequence_splitter/knowledge_base.py`: 完全重写，支持目录和文件两种模式
- `operation_sequence_splitter/splitter.py`: 更新以适配新的知识库接口
- `main.py`: 更新帮助文本和路径验证逻辑
- `config.example.json`: 更新默认知识库路径
- `operation_sequence_splitter/config.py`: 更新默认配置

### 新增文件

- `data/knowledge_base_example/`: 新的知识库格式示例目录
  - `operation_001.json`: 登录系统示例
  - `operation_002.json`: 查看用户信息示例
  - `operation_003.json`: 创建新任务示例
- `test_new_knowledge_base.py`: 新格式测试脚本
- `KNOWLEDGE_BASE_FORMAT.md`: 知识库格式详细文档

### 使用说明

#### 目录模式（推荐）

```bash
python main.py -i "操作序列" -k data/knowledge_base_example
```

#### 单文件模式（兼容旧格式）

```bash
python main.py -i "操作序列" -k data/manual.example.json
```

### 迁移指南

如果您之前使用单文件格式，可以：

1. **继续使用**：单文件格式仍然完全支持
2. **迁移到目录模式**：
   - 将每个操作拆分为单独的JSON文件
   - 按照新格式定义操作信息
   - 将所有文件放在一个目录下
   - 更新配置文件中的路径

参考 `KNOWLEDGE_BASE_FORMAT.md` 了解详细的格式说明。

