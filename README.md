# 南京房地产数据展示网站（Spring Boot + Python）

按你的最新要求，项目默认使用 **Maven 本地启动**，不再依赖 Docker。

## 0. 版本适配说明

当前项目已验证并约束以下版本范围：
- Apache Maven **3.8.7+**
- OpenJDK **17 ~ 21**（你提供的 `openjdk 21.0.10` 在支持范围内）

`pom.xml` 已加入 Maven/Java 版本校验规则，环境不匹配时会在构建阶段直接报错。

## 1. 环境准备（WSL）

在 WSL 终端中确认：

```bash
java -version
mvn -version
python3 --version
```

建议：
- Java 17+
- Maven 3.9+
- Python 3.10+

## 2. 启动网站（Maven）

进入项目目录：

```bash
cd /workspace/codex
```

执行启动：

```bash
mvn spring-boot:run
```

启动后访问：
- 页面：http://localhost:8080
- API：http://localhost:8080/api/prices

## 3. 更新南京小区房价数据（Python 爬虫）

运行爬虫（脚本仅依赖 Python 标准库，无需额外 pip 安装）：

```bash
python3 python/crawler_nanjing_prices.py --max-pages 3 --output data/nanjing_prices.json
# 如果网络被限制，会自动回退到 src/main/resources/data/nanjing_prices.json
```


### 3.1 如果出现 403（代理拦截）怎么办？

可以用以下两种方式：

1. 指定可用代理：

```bash
python3 python/crawler_nanjing_prices.py --max-pages 3 --proxy http://127.0.0.1:7890 --output data/nanjing_prices.json
```

2. 使用离线 HTML 验证解析流程（适合当前网络受限环境）：

```bash
python3 python/crawler_nanjing_prices.py --offline-html python/sample_lianjia_page.html --output data/nanjing_prices.json
```

无论在线抓取还是离线解析，只要结果为空，脚本都会自动回退到 `src/main/resources/data/nanjing_prices.json`。

## 4. 让 Maven 启动的 Java 应用读取爬虫输出文件

默认配置支持从环境变量读取数据文件路径（`APP_DATA_FILE`），建议这样启动：

```bash
export APP_DATA_FILE=data/nanjing_prices.json
mvn spring-boot:run
```

如果不设置 `APP_DATA_FILE`，应用会读取默认路径 `data/nanjing_prices.json`；
若默认路径不存在，会自动回退到内置示例数据 `src/main/resources/data/nanjing_prices.json`。

## 5. 项目结构

- `src/main/java/...`：Spring Boot 代码
- `src/main/resources/templates/index.html`：简约风页面
- `src/main/resources/data/nanjing_prices.json`：内置兜底数据
- `data/nanjing_prices.json`：爬虫输出数据
- `python/crawler_nanjing_prices.py`：南京小区房价爬虫

## 6. 注意事项

- 爬虫仅用于学习演示，请遵守目标网站 robots、服务条款和相关法律法规。
- 当前版本仅抓取并展示南京各小区房价。
