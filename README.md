# 南京房地产数据展示网站（Java + Python + Docker）

一个可本地运行的简约风网站：
- Java（Spring Boot + Thymeleaf）用于展示数据
- Python 爬虫用于抓取南京小区房价并写入 JSON
- Docker Compose 支持一键容器化部署（适合 WSL）

---

## 1. 一键容器化部署（推荐，WSL）

> 适用于：Windows + WSL2 + Docker Desktop

### 1.1 前置条件

1. 已安装 **Docker Desktop**，并开启 **Use the WSL 2 based engine**。
2. 在 Docker Desktop 的 `Settings -> Resources -> WSL Integration` 中打开你当前发行版（如 Ubuntu）。
3. 在 WSL 终端验证：

```bash
docker --version
docker compose version
```

### 1.2 进入项目目录

```bash
cd /workspace/codex
```

### 1.3 一键启动网站

```bash
docker compose up --build -d app
```

启动后访问：
- 页面：http://localhost:8080
- API：http://localhost:8080/api/prices

### 1.4 一键抓取并更新南京房价数据

```bash
docker compose --profile crawler run --rm crawler
```

该命令会把最新抓取结果写入：

`data/nanjing_prices.json`

因为 `app` 容器挂载了 `./data:/app/data`，应用会读取该文件（`APP_DATA_FILE=/app/data/nanjing_prices.json`）。

### 1.5 常用运维命令

查看日志：

```bash
docker compose logs -f app
```

重启服务：

```bash
docker compose restart app
```

停止并清理：

```bash
docker compose down
```

---

## 2. 不用 Docker 的本地运行方式（可选）

### 2.1 启动 Java 网站

```bash
mvn spring-boot:run
```

### 2.2 运行 Python 爬虫更新数据

```bash
python3 -m pip install -r requirements.txt
python3 python/crawler_nanjing_prices.py --max-pages 3 --output data/nanjing_prices.json
```

如果你希望 Java 进程读取 `data/nanjing_prices.json`，可设置：

```bash
export APP_DATA_FILE=data/nanjing_prices.json
mvn spring-boot:run
```

---

## 3. 项目结构

- `src/main/java/...`：Spring Boot 代码
- `src/main/resources/templates/index.html`：简约风页面
- `src/main/resources/data/nanjing_prices.json`：内置兜底数据
- `data/nanjing_prices.json`：容器与本地共享数据（爬虫输出）
- `python/crawler_nanjing_prices.py`：南京小区房价爬虫
- `docker-compose.yml`：一键部署编排
- `Dockerfile`：应用镜像构建

---

## 4. 注意事项

- 爬虫仅用于学习演示，请遵守目标网站 robots、服务条款和相关法律法规。
- 当前版本仅抓取并展示南京各小区房价。
