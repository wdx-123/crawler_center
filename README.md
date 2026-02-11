# crawler_center

`crawler_center` 是一个基于 **FastAPI** 的轻量爬虫聚合服务，当前支持：

- 抓取 **LeetCode 中国站**用户公开信息（基础信息、最近 AC、提交统计等）
- 抓取 **洛谷（Luogu）** 用户练题数据
- 通过统一的 HTTP API 对外提供数据

---

## 目录结构

```text
crawler_center/
├─ crawler_center/
│  ├─ api/
│  │  ├─ main.py
│  │  └─ schemas.py
│  ├─ config.py
│  ├─ leetcode_client.py
│  ├─ leetcode_types.py
│  └─ luogu_client.py
├─ config.yaml
├─ requirements.txt
├─ Dockerfile
└─ docker-compose.yml
```

---

## 功能概览

### 健康检查

- `GET /healthz`

### LeetCode 接口

- `POST /leetcode/profile_meta`：用户主页元信息（是否存在、标题、描述等）
- `POST /leetcode/recent_ac`：最近 AC 记录
- `POST /leetcode/submit_stats`：提交与做题统计
- `POST /leetcode/public_profile`：公开个人资料
- `POST /leetcode/crawl`：聚合抓取（meta + recent_ac + stats）

### Luogu 接口

- `POST /luogu/practice`：用户通过题目列表与计数

---

## 运行环境

- Python `3.12+`（当前项目使用过 `3.12.5`）
- 依赖见 `requirements.txt`

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 本地启动（推荐）

在仓库根目录执行：

```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn crawler_center.api.main:app --host 0.0.0.0 --port 8001 --reload
```

服务启动后访问：

- Swagger UI: `http://127.0.0.1:8001/docs`
- OpenAPI: `http://127.0.0.1:8001/openapi.json`

---

## Docker 部署

### 方式一：docker run

```bash
docker build -t crawler_center:latest .
docker run -d --name crawler_center \
  -p 8001:8001 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  crawler_center:latest
```

### 方式二：docker compose

```bash
docker compose up -d
```

默认端口为 `8001`，可在 `docker-compose.yml` 中修改映射。

---

## 配置说明

项目通过根目录 `config.yaml` 读取配置，示例：

```yaml
leetcode:
  base_url: "https://leetcode.cn"

luogu:
  base_url: "https://www.luogu.com.cn"

crawler:
  default_timeout: 15
  default_sleep_sec: 0.8
  default_user_agent: "Mozilla/5.0 (...)"

api:
  title: "crawler_center"
  version: "0.1.0"
```

说明：

- `default_timeout`：请求超时时间（秒）
- `default_sleep_sec`：每次请求前休眠秒数，用于降低访问频率
- `default_user_agent`：HTTP 请求 UA

---

## API 调用示例

> 以下示例默认服务地址为 `http://127.0.0.1:8001`

### 1) 健康检查

```bash
curl http://127.0.0.1:8001/healthz
```

### 2) LeetCode 用户主页元信息

```bash
curl -X POST "http://127.0.0.1:8001/leetcode/profile_meta" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"leetcode\",\"sleep_sec\":0}"
```

### 3) LeetCode 最近 AC

```bash
curl -X POST "http://127.0.0.1:8001/leetcode/recent_ac" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"leetcode\",\"sleep_sec\":0}"
```

### 4) LeetCode 提交统计

```bash
curl -X POST "http://127.0.0.1:8001/leetcode/submit_stats" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"leetcode\",\"sleep_sec\":0}"
```

### 5) LeetCode 公开资料

```bash
curl -X POST "http://127.0.0.1:8001/leetcode/public_profile" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"leetcode\",\"sleep_sec\":0}"
```

### 6) LeetCode 聚合抓取

```bash
curl -X POST "http://127.0.0.1:8001/leetcode/crawl" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"leetcode\",\"sleep_sec\":0}"
```

### 7) Luogu 练题数据

```bash
curl -X POST "http://127.0.0.1:8001/luogu/practice" \
  -H "Content-Type: application/json" \
  -d "{\"uid\":1,\"sleep_sec\":0}"
```

---

## 响应结构

成功响应统一结构：

```json
{
  "ok": true,
  "data": {}
}
```

参数校验失败（FastAPI 默认）通常返回 `422`：

```json
{
  "detail": [...]
}
```

---

## 常见问题

### 1) 启动时报找不到配置文件

- 确保 `config.yaml` 位于仓库根目录
- 或者确保运行目录与 `config.yaml` 路径一致

### 2) 接口返回空数据

- 目标用户可能不存在、无公开数据，或站点返回策略变更
- 可先调用 `profile_meta` 判断用户页面是否可访问

### 3) 抓取不稳定

- 适当增加 `sleep_sec`
- 调整 `default_timeout`
- 检查网络连通性与目标站点可访问性

---

## 发布到 GitHub 建议

提交前建议：

- 确认 `.venv/`、`__pycache__/`、IDE 配置目录未被提交
- 检查 `config.yaml` 中是否包含敏感信息（如后续扩展了私密配置）
- 在 GitHub 仓库中补充 Topics、Description、License

---

## License

如需开源，建议补充 `LICENSE` 文件（例如 MIT License）。
