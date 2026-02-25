# 项目命名规范 (PEP 8)

本文档定义项目的目录、文件和代码级命名规范，所有新增与重构必须遵循。

## 1. 目录与文件命名

### 1.1 项目根目录
- 优先使用小写字母和连字符（kebab-case），如 `my-awesome-python-project`

### 1.2 Python 包（目录）
- **必须**全小写，可用下划线提高可读性
- **严禁**使用连字符（连字符无法被 Python `import`）
- 示例：`user_service/`, `data_models/`, `graph_api/`

### 1.3 Python 模块/文件
- **必须**使用 `snake_case`（全小写 + 下划线）
- **严禁**使用驼峰命名
- 示例：`database_client.py`, `utils.py`

### 1.4 测试文件
- 必须以 `test_` 为前缀，便于 pytest 自动发现
- 示例：`test_database_client.py`

### 1.5 配置与静态资源
- 保持行业标准全小写，如 `pyproject.toml`, `docker-compose.yml`

## 2. 代码级命名 (PEP 8)

| 类型 | 规范 | 示例 |
|------|------|------|
| 类、异常 | `PascalCase` | `UserProfile`, `DatabaseConnectionError` |
| 函数、方法、变量 | `snake_case` | `calculate_total_price()`, `user_count` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 受保护/私有成员 | 单下划线前缀 | `_internal_cache`, `_validate_data()` |
| 关键字冲突 | 末尾加下划线 | `class_`, `id_` |

## 3. 导入规范

- **导入顺序**：标准库 → 第三方库 → 本地模块（遵循 `isort`）
- **优先绝对导入**：`from src.models.user import User`
- **减少相对导入**：避免易混淆的 `from ..user import User`

## 4. 执行规则

- 创建新文件/目录前必须进行「命名合规性检查」
- 需求中的不规范命名应自动纠正后执行
- 修改已有不规范代码时，主动提出重命名建议并更新所有相关 `import`

## 5. 已完成的规范化重命名（参考）

详见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 的「命名修正记录」。
