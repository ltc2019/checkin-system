# 打卡签到系统

早起 · 读书 · 运动 · 遇见更好的自己

一个美观的 Web H5 打卡系统，支持早起、读书、运动三项打卡，包含统计分析、排行榜、人员管理等功能。

## 功能特色

- 🌅 **早起打卡** - 5:30-8:30 时间校验，连续打卡天数统计
- 📚 **读书打卡** - 录音朗读 + 心得分享 + 书籍管理
- 🏃 **运动打卡** - 步数记录 + 拍照/视频打卡
- 📊 **统计分析** - 周/月/年单项和总打卡次数图表
- 🏆 **排行榜** - 总榜 + 单项榜，积分系统
- 👥 **人员管理** - 用户增删改，角色权限
- ⚙️ **规则配置** - 打卡时间、积分奖励、必填项
- 🎨 **顶级配色** - 渐变紫蓝主题，深色模式
- 🎉 **打卡成功弹窗** - 随机场景图 + 一键分享

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Tailwind CSS + Chart.js |
| 后端 | Python FastAPI |
| 数据库 | SQLite |
| 认证 | JWT Token |

## 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/ltc2019/checkin-system.git
cd checkin-system
```

### 2. 后端部署

```bash
cd backend

# 安装依赖
pip3 install -r requirements.txt

# 启动服务
python3 -m uvicorn app.main:app --reload --port 8000
```

后端默认运行在 `http://localhost:8000`

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

前端默认运行在 `http://localhost:3000`

### 4. 生产部署

使用 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/checkin-system/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 上传文件
    location /uploads {
        alias /path/to/checkin-system/uploads;
    }
}
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |

⚠️ **生产环境请立即修改默认密码**

## 使用说明

### 早起打卡

1. 进入「早起」页面
2. 系统自动检测当前时间（仅 5:30-8:30 可打卡）
3. 输入今日寄语（可选）
4. 点击「立即打卡」
5. 弹出成功弹窗，可分享到社交平台

### 读书打卡

1. 进入「读书」页面
2. 选择书籍（可先在「书籍管理」添加）
3. 点击「开始录音」朗读片段
4. 输入读书心得
5. 点击「提交打卡」

### 运动打卡

1. 进入「运动」页面
2. 选择运动类型
3. 输入今日步数
4. 上传照片或视频（必填）
5. 点击「提交打卡」

### 统计分析

- 进入「统计」页面
- 切换周/月/年查看数据
- 查看单项统计柱状图
- 查看趋势折线图

### 排行榜

- 进入「排行」页面
- 切换周榜/月榜/年榜
- 查看总榜或单项榜

### 管理后台（管理员）

- 进入「管理」页面
- **人员管理**：添加/删除用户，设置角色
- **规则配置**：打卡时间范围、积分奖励、必填项

## API 接口

### 认证

```
POST /api/auth/login      # 登录
POST /api/auth/register   # 注册
GET  /api/auth/me         # 当前用户信息
```

### 打卡

```
POST /api/checkin/early   # 早起打卡
POST /api/checkin/reading # 读书打卡
POST /api/checkin/sport   # 运动打卡
GET  /api/checkin/today   # 今日打卡状态
POST /api/checkin/upload  # 上传文件
```

### 书籍

```
GET  /api/books           # 书籍列表
POST /api/books           # 添加书籍
PUT  /api/books/{id}      # 更新书籍
DELETE /api/books/{id}    # 删除书籍
```

### 统计

```
GET /api/stats/weekly     # 周统计
GET /api/stats/monthly    # 月统计
GET /api/stats/yearly     # 年统计
GET /api/stats/rank       # 排行榜
```

### 管理

```
GET  /api/admin/users     # 用户列表
POST /api/admin/users     # 添加用户
PUT  /api/admin/users/{id}  # 更新用户
DELETE /api/admin/users/{id} # 删除用户
GET  /api/admin/rules     # 规则列表
PUT  /api/admin/rules/{type} # 更新规则
```

## 目录结构

```
checkin-system/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── database.py       # SQLite 数据库
│   │   ├── routers/          # API 路由
│   │   ├── models/           # 数据模型
│   │   └── utils/            # 工具函数
│   ├── requirements.txt
│   └── checkin.db            # 数据库文件
├── frontend/
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── stores/           # Pinia 状态
│   │   ├── router/           # 路由配置
│   │   └── style.css         # 全局样式
│   ├── package.json
│   └── vite.config.js
├── uploads/                  # 上传文件存储
│   ├── audio/
│   ├── photos/
│   └── videos/
└── README.md
```

## 配色方案

| 类型 | 颜色 |
|------|------|
| 主色 | `#667eea → #764ba2` 渐变紫蓝 |
| 早起 | `#f6d365 → #fda085` 日出橙 |
| 读书 | `#11998e → #38ef7d` 知识绿 |
| 运动 | `#4facfe → #00f2fe` 活力蓝 |
| 金牌 | `#ffd700` 金色 |
| 背景 | `#0f0f23` 深色 |

## 常见问题

### Q: 打卡时间不对？

修改规则配置：管理员进入「管理」→「规则」→ 修改时间范围

### Q: 如何修改积分？

管理员进入「管理」→「规则」→ 修改各项积分值

### Q: 如何备份数据？

```bash
# 备份数据库
cp backend/checkin.db backup/checkin_$(date +%Y%m%d).db

# 备份上传文件
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz uploads/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

Made with ❤️ by Claude Code