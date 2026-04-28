# 南京房地产数据展示网站（Java + Python）

一个可本地运行的简约风网站：
- Java（Spring Boot + Thymeleaf）用于展示数据
- Python 爬虫用于抓取南京小区房价并写入 JSON

## 1. 本地运行网站

```bash
mvn spring-boot:run
```

打开：`http://localhost:8080`

API：`http://localhost:8080/api/prices`

## 2. 运行爬虫更新数据

先安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

执行爬虫：

```bash
python3 python/crawler_nanjing_prices.py --max-pages 3
```

输出文件默认为：

`src/main/resources/data/nanjing_prices.json`

## 3. 技术说明

- 前端采用单页面表格展示，风格简约、轻量。
- Java 读取 JSON 后按均价降序展示。
- 爬虫默认抓取链家南京小区页，若页面结构变化可在 `SELECTORS` 中调整 CSS 选择器。

## 4. 注意事项

- 爬虫仅用于学习演示，请遵守目标网站 robots、服务条款和相关法律法规。
- 当前示例仅覆盖南京各小区均价数据。
