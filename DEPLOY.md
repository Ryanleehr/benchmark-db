## 环境要求

- 操作系统：Ubuntu 22.04 / 24.04（或其他支持 Docker 的 Linux 发行版）
- Docker Engine
- Docker Compose v2

### 安装 Docker

```bash
sudo apt update
sudo apt install -y docker.io
```

注意：`docker.io` 包只包含 Docker 引擎，不含 Compose 插件。直接运行 `docker compose` 会报
`unknown shorthand flag: 'd' in -d`，需要单独安装：

```bash
sudo apt install -y docker-compose-v2
```

### 配置免 sudo 运行

默认情况下 Docker 命令需要 root 权限。将当前用户加入 docker 组：

```bash
sudo usermod -aG docker $USER
```

用户组变更需要重新登录才生效。退出当前会话再重新进入，然后验证：

```bash
docker ps
```

如果不加 `sudo` 能正常输出容器列表（初次安装时为空表），说明配置成功。

## 部署步骤

### 1. 获取代码

```bash
git clone https://github.com/Ryanleehr/benchmark-db.git
cd benchmark-db
```

### 2. 创建环境变量文件

仓库中只包含模板文件 `.env.example`，真实的 `.env` 不进版本控制，需要手动创建：

```bash
cp .env.example .env
```

### 3. 设置 API 密钥

生成一个随机 token：

```bash
openssl rand -hex 16
```

编辑 `.env`，把输出的字符串填入 `API_TOKEN`：


这个值由部署者自行决定，服务端校验和客户端请求使用同一个值即可。

### 4. 构建并启动

```bash
docker compose up -d --build
```

首次构建需要下载基础镜像并安装依赖，约需 2-3 分钟。

## 数据初始化

数据库文件 `data/benchmark.db` 不在版本控制中（见 `.gitignore`），首次部署需要手动初始化。

以下脚本在宿主机执行（非容器内），需要先准备 Python 环境：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

按顺序执行以下四步：

### 1. 创建表结构

```bash
python src/init_db.py
```

创建 `companies`、`financials`、`headcount` 三张表。脚本使用 `CREATE TABLE IF NOT EXISTS`，可重复执行。

### 2. 导入公司清单

```bash
python src/load_companies.py
```

从 `data/companies.csv` 读取 8 家对标公司，并补充赛道分类字段。

### 3. 导入员工人数

```bash
python src/load_headcount.py
```

从 `data/headcount.csv` 读取手工维护的员工人数数据。该数据摘自各公司年报"员工情况"章节，每条记录保留来源标注。

### 4. 抓取财务数据

```bash
python src/sync.py
```

从新浪财经接口抓取 8 家公司的全部历史财报，约 380 条记录，耗时 10-20 秒。

以上四个脚本均为幂等设计，重复执行不会产生重复数据。

## 验证部署

### 1. 检查容器状态

```bash
docker compose ps
```

`STATUS` 列应显示 `Up`，`PORTS` 列应显示 `0.0.0.0:8000->8000/tcp`。
若显示 `Exited` 或 `Restarting`，说明启动失败，需查看日志排查。

### 2. 健康检查

```bash
curl http://localhost:8000/health
```

预期返回 `{"status":"ok"}`。该接口无需鉴权，只验证服务进程是否正常响应。

### 3. 数据与鉴权验证

先确认开放接口能返回数据：

```bash
curl http://localhost:8000/companies
```

预期返回 8 家公司的 JSON 数组。该接口无需鉴权。

再验证鉴权接口：

```bash
curl -i -H "Authorization: Bearer <你的 API_TOKEN>" http://localhost:8000/metrics/603866
```

预期返回 200 和桃李面包历年指标。若 token 填错会返回 403，可以用一个错误值测试一次，
确认鉴权确实生效。

### 交互式文档

浏览器访问 `http://localhost:8000/docs`，可以看到全部接口列表并直接测试。

## 常见问题

### `unknown shorthand flag: 'd' in -d`

`docker.io` 包只包含 Docker 引擎，不含 Compose 插件。单独安装：

```bash
sudo apt install -y docker-compose-v2
```

### `ModuleNotFoundError: No module named 'log_config'`

Python 从启动位置查找模块，而容器以 `/app` 为工作目录，`src/` 目录下的模块无法被直接导入。
Dockerfile 中已通过 `ENV PYTHONPATH=/app/src` 解决。若自行修改了 Dockerfile，请确认该行存在。

### `curl: (56) Recv failure: Connection reset by peer`

容器启动需要几秒钟完成应用初始化，在此之前发起请求会被拒绝。等待 5-10 秒后重试即可。
可用以下命令确认服务已就绪：

```bash
docker compose logs --tail 5
```

看到 `Application startup complete.` 表示可以开始请求。

### 日志时间戳与本地时间相差 8 小时

容器默认使用 UTC 时区。Dockerfile 中已通过 `ENV TZ=Asia/Shanghai` 设置为北京时间。
注意定时任务的时区由 APScheduler 的 `timezone` 参数单独控制，两者需要保持一致。

### `attempt to write a readonly database`

容器内进程以 root 身份运行，它在挂载卷中创建的文件属主为 root，宿主机普通用户无写入权限。
若需要在宿主机上操作数据库文件，先修改属主：

```bash
sudo chown $USER:$USER data/benchmark.db
```

或删除后重新初始化：

```bash
sudo rm data/benchmark.db
python src/init_db.py
```

### `no such table: companies`

数据库文件存在但表结构未创建。SQLite 在文件不存在时会自动创建空文件，不会报错，
因此这个问题通常出现在首次部署跳过初始化步骤的情况下。

按「数据初始化」一节的四个步骤依次执行即可。

### 端口 8000 已被占用

修改 `docker-compose.yml` 中的端口映射，将宿主机端口改为其他值：

```yaml
    ports:
      - "8080:8000"
```

冒号左侧是宿主机端口，右侧是容器内端口，只需修改左侧。

## 日常运维

### 查看日志

```bash
docker compose logs --tail 50
```

持续跟踪日志（按 Ctrl+C 退出）：

```bash
docker compose logs -f
```

抓取和同步的日志同时写入 `logs/` 目录，可直接查看：

```bash
cat logs/sync.log
cat logs/fetcher.log
```

### 重启服务

```bash
docker compose restart
```

### 停止与启动

```bash
docker compose stop
docker compose start
```

完全移除容器（数据不受影响，因为 `data/` 是挂载目录）：

```bash
docker compose down
```

### 更新代码后重新部署

```bash
git pull
docker compose up -d --build
```

`--build` 会重新构建镜像。若只修改了配置未改代码，可省略该参数。

### 手动触发数据同步

服务内置每日 02:00 自动同步。如需立即执行：

```bash
curl -X POST -H "Authorization: Bearer <你的 API_TOKEN>" http://localhost:8000/sync
```

返回示例：

```json
{"written": 381, "failed": []}
```

`failed` 数组列出同步失败的公司名称，正常情况下为空。

### 更新员工人数数据

员工人数为手工维护，每年年报发布后需要更新：

1. 编辑 `data/headcount.csv`，补充新一年的数据，`source` 列填写数据出处
2. 执行导入：

```bash
python src/load_headcount.py
```

### 数据备份

数据库为单个 SQLite 文件，直接复制即可备份：

```bash
cp data/benchmark.db data/benchmark.db.$(date +%Y%m%d)
```