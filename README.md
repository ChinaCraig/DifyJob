# Dify任务调度系统

这是一个基于Flask的定时任务调度系统，主要用于定时调用Dify工作流API。

## 功能特性

- ✅ 定时任务调度：支持设置任务执行间隔（分钟）
- ✅ 时间范围管理：自动计算起始时间和结束时间
- ✅ 任务日志记录：记录每次执行的详细信息
- ✅ Web管理界面：简洁美观的任务配置和监控界面
- ✅ 任务控制：支持启动、停止、立即执行任务
- ✅ 灵活配置：支持自定义开始时间或使用上次结束时间
- ✅ 配置化管理：所有配置项统一在config.env文件中管理
- ✅ 动态配置：前端自动从服务器获取配置参数

## 系统架构

```
WeChatJOB/
├── app/                    # 应用主目录
│   ├── __init__.py        # Flask应用初始化
│   ├── config.py          # 配置管理模块
│   ├── models.py          # 数据库模型
│   ├── routes.py          # 路由定义
│   ├── services.py        # 业务逻辑服务
│   └── templates/         # HTML模板
│       ├── base.html      # 基础模板
│       ├── index.html     # 主页
│       └── logs.html      # 日志页面
├── database/              # 数据库相关
│   └── create_tables.sql  # 建表语句
├── requirements.txt       # Python依赖
├── run.py                # 应用启动文件
├── config.env            # 环境变量配置
├── start.sh              # 启动脚本
├── verify_config.py      # 配置验证脚本
└── README.md             # 项目说明
```

## 配置管理

### 配置文件说明

所有配置项都在 `config.env` 文件中统一管理，包括：

#### Flask运行配置
```env
FLASK_DEBUG=True                    # 调试模式
FLASK_HOST=0.0.0.0                 # 监听地址
FLASK_PORT=5001                     # 监听端口
FLASK_USE_RELOADER=False            # 是否使用重载器
```

#### 数据库配置
```env
DB_HOST=192.168.16.105              # 数据库主机
DB_PORT=3306                        # 数据库端口
DB_USER=root                        # 数据库用户名
DB_PASSWORD=your_password           # 数据库密码
DB_NAME=wechat_job                  # 数据库名称
```

#### Dify API配置
```env
DIFY_API_URL=http://localhost/v1/workflows/run  # Dify API地址
DIFY_API_KEY=your-dify-api-key-here            # Dify API密钥
DIFY_API_TIMEOUT=30                            # API请求超时时间(秒)
DIFY_USER_IDENTIFIER=wechat-job-system         # API用户标识
```

#### 系统配置
```env
LOG_LEVEL=INFO                      # 日志级别
LOGS_PER_PAGE_DEFAULT=10            # 默认分页大小
LOGS_PER_PAGE_MAX=50                # 最大分页大小
AUTO_REFRESH_INTERVAL_SECONDS=30    # 自动刷新间隔(秒)
NEAR_EXECUTION_REFRESH_SECONDS=5    # 接近执行时刷新间隔(秒)
```

### 配置验证

运行配置验证脚本检查所有配置是否正确：

```bash
python3 verify_config.py
```

该脚本会验证：
- 配置文件是否存在
- 所有配置项是否正确加载
- Flask应用是否能正常创建
- API端点是否正常工作

## 安装部署

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

连接到MySQL数据库并执行建表语句：

```bash
mysql -h 192.168.16.105 -P 3306 -u root -p19900114xin < database/create_tables.sql
```

### 4. 配置环境变量

编辑 `config.env` 文件，配置你的参数：

```env
# 必须配置的项目
DB_PASSWORD=your_actual_password
DIFY_API_KEY=your-actual-dify-api-key

# 可选配置项（有默认值）
FLASK_PORT=5001
LOG_LEVEL=INFO
```

### 5. 启动应用

使用启动脚本（推荐）：
```bash
./start.sh
```

或直接运行：
```bash
python3 run.py
```

应用将根据配置文件中的设置启动，默认地址：`http://localhost:5001`

## 使用说明

### 1. 配置任务

1. 访问主页：`http://localhost:5001`
2. 在"任务配置"区域设置：
   - 执行间隔（分钟）
   - Dify API Key
   - Dify API URL
3. 点击"保存配置"

### 2. 启动任务

1. 在"任务控制"区域：
   - 可选择指定开始时间，或留空使用上次结束时间
   - 点击"启动任务"开始定时执行
   - 点击"停止任务"停止定时执行
   - 点击"立即执行"手动触发一次任务

### 3. 查看日志

- 主页显示最近10条执行日志
- 点击"查看全部日志"查看完整日志列表
- 点击"详情"查看单条日志的详细信息

## API接口

### 配置管理

- `GET /api/config` - 获取当前配置
- `POST /api/config` - 更新配置

### 任务控制

- `POST /api/task/start` - 启动任务
- `POST /api/task/stop` - 停止任务
- `POST /api/task/execute` - 立即执行任务

### 日志查询

- `GET /api/logs` - 获取执行日志（支持分页）

## 数据库表结构

### task_configs（任务配置表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| interval_minutes | INT | 间隔时间(分钟) |
| is_active | BOOLEAN | 是否启用 |
| last_end_time | DATETIME | 最后结束时间 |
| dify_api_key | VARCHAR(255) | Dify API Key |
| dify_url | VARCHAR(500) | Dify API URL |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### task_logs（任务执行日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| interval_minutes | INT | 间隔时间(分钟) |
| execute_time | DATETIME | 执行时间 |
| start_time | DATETIME | 起始时间 |
| end_time | DATETIME | 结束时间 |
| status | VARCHAR(20) | 执行状态 |
| response_data | TEXT | 响应数据 |
| error_message | TEXT | 错误信息 |
| created_at | DATETIME | 创建时间 |

## 工作原理

1. **时间计算**：
   - 首次启动：使用指定的开始时间，或当前时间减去间隔时间
   - 后续执行：使用上次的结束时间作为新的开始时间
   - 结束时间 = 开始时间 + 间隔时间

2. **API调用**：
   - 将起始时间和结束时间作为参数传递给Dify工作流
   - 使用Bearer Token认证
   - 支持流式响应模式

3. **日志记录**：
   - 每次执行都记录完整的执行信息
   - 包括成功响应数据或失败错误信息
   - 支持通过Web界面查看和分页

## 注意事项

1. 确保MySQL数据库连接正常
2. 配置正确的Dify API Key和URL
3. 定时任务在应用重启后会自动恢复（如果之前是启用状态）
4. 建议在生产环境中使用更安全的密钥管理方式

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库连接参数是否正确

2. **Dify API调用失败**
   - 检查API Key是否正确
   - 验证API URL是否可访问
   - 查看错误日志获取详细信息

3. **定时任务不执行**
   - 确认任务状态为"运行中"
   - 检查应用日志是否有错误信息
   - 验证调度器是否正常启动

## 开发说明

### 技术栈

- **后端**：Flask + SQLAlchemy + APScheduler
- **前端**：Bootstrap 5 + Axios
- **数据库**：MySQL 8.0
- **定时任务**：APScheduler

### 扩展开发

如需扩展功能，可以：

1. 在 `app/models.py` 中添加新的数据模型
2. 在 `app/services.py` 中添加业务逻辑
3. 在 `app/routes.py` 中添加新的API接口
4. 在 `app/templates/` 中添加新的页面模板

## 许可证

MIT License 