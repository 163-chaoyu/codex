#!/usr/bin/env python3
"""抓取南京小区房价并保存为 JSON。

说明：
1) 优先尝试抓取链家南京小区页（urllib + 正则）。
2) 支持自定义代理与离线 HTML 文件，适配受限网络环境。
3) 若抓取为空，会自动回退到本地样例数据，确保输出非空。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

DEFAULT_BASE_URL = "https://nj.lianjia.com/xiaoqu/pg{page}/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

ITEM_RE = re.compile(r"<li[^>]*xiaoquListItem[^>]*>(.*?)</li>", re.S)
NAME_RE = re.compile(r"<div[^>]*class=\"title\"[^>]*>\s*<a[^>]*>([^<]+)</a>", re.S)
DISTRICT_RE = re.compile(r"class=\"district\"[^>]*>([^<]+)<", re.S)
PRICE_RE = re.compile(r"class=\"xiaoquListItemPrice\"[^>]*>\s*<span[^>]*>(\d+)</span>", re.S)


@dataclass
class CommunityPrice:
    communityName: str
    district: str
    avgUnitPrice: int
    source: str
    crawlDate: str


def build_opener(proxy: str | None) -> urllib.request.OpenerDirector:
    if proxy:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    return urllib.request.build_opener()


def fetch_html(url: str, opener: urllib.request.OpenerDirector, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_communities(html: str, crawl_date: str, source: str) -> list[CommunityPrice]:
    output: list[CommunityPrice] = []
    for block in ITEM_RE.findall(html):
        name_match = NAME_RE.search(block)
        price_match = PRICE_RE.search(block)
        if not name_match or not price_match:
            continue

        district_match = DISTRICT_RE.search(block)
        output.append(
            CommunityPrice(
                communityName=name_match.group(1).strip(),
                district=(district_match.group(1).strip() if district_match else "未知"),
                avgUnitPrice=int(price_match.group(1)),
                source=source,
                crawlDate=crawl_date,
            )
        )
    return output


def crawl(max_pages: int, sleep_max: float, base_url: str, proxy: str | None) -> list[CommunityPrice]:
    crawl_date = dt.date.today().isoformat()
    all_rows: list[CommunityPrice] = []
    opener = build_opener(proxy)

    for page in range(1, max_pages + 1):
        url = base_url.format(page=page)
        try:
            print(f"[INFO] crawling page {page}: {url}")
            html = fetch_html(url, opener=opener)
            rows = parse_communities(html, crawl_date, source=url)
            print(f"[INFO] parsed rows in page {page}: {len(rows)}")
            if not rows:
                break
            all_rows.extend(rows)
            time.sleep(random.uniform(0.5, sleep_max))
        except (urllib.error.URLError, TimeoutError, ValueError) as ex:
            print(f"[WARN] crawl failed on page {page}: {ex}")
            if isinstance(ex, urllib.error.URLError) and "403" in str(ex):
                print("[HINT] Detected 403. Try --proxy http://<proxy-host>:<proxy-port>")
            break

    dedup = deduplicate_rows(all_rows)
    dedup.sort(key=lambda x: x.avgUnitPrice, reverse=True)
    return dedup


def deduplicate_rows(rows: Iterable[CommunityPrice]) -> list[CommunityPrice]:
    seen: set[str] = set()
    output: list[CommunityPrice] = []
    for row in rows:
        key = f"{row.communityName}-{row.district}"
        if key in seen or row.avgUnitPrice <= 0:
            continue
        seen.add(key)
        output.append(row)
    return output


def load_fallback_data(path: Path) -> list[CommunityPrice]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    today = dt.date.today().isoformat()
    rows = [CommunityPrice(**item) for item in raw]
    for row in rows:
        row.crawlDate = today
        row.source = f"{row.source} (fallback)"
    return rows


def parse_offline_html(path: Path) -> list[CommunityPrice]:
    if not path.exists():
        return []
    crawl_date = dt.date.today().isoformat()
    html = path.read_text(encoding="utf-8", errors="ignore")
    rows = parse_communities(html, crawl_date, source=f"file://{path}")
    rows = deduplicate_rows(rows)
    rows.sort(key=lambda x: x.avgUnitPrice, reverse=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取南京小区房价")
    parser.add_argument("--max-pages", type=int, default=2, help="抓取页数")
    parser.add_argument(
        "--base-url",
        type=str,
        default=DEFAULT_BASE_URL,
        help="抓取页 URL 模板，需包含 {page} 占位符",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="可选代理，例如 http://127.0.0.1:7890",
    )
    parser.add_argument(
        "--offline-html",
        type=Path,
        default=None,
        help="离线 HTML 文件路径（用于代理受限环境测试）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/nanjing_prices.json"),
        help="输出 JSON 文件路径",
    )
    parser.add_argument("--sleep-max", type=float, default=1.3, help="每页抓取后的随机等待上限（秒）")
    parser.add_argument(
        "--fallback-file",
        type=Path,
        default=Path("src/main/resources/data/nanjing_prices.json"),
        help="抓取失败时的回退数据文件",
    )
    args = parser.parse_args()

    if args.offline_html:
        rows = parse_offline_html(args.offline_html)
    else:
        rows = crawl(
            max_pages=args.max_pages,
            sleep_max=args.sleep_max,
            base_url=args.base_url,
            proxy=args.proxy,
        )

    if not rows:
        print("[WARN] no online/offline rows fetched, fallback to local sample data")
        rows = load_fallback_data(args.fallback_file)

    if not rows:
        raise SystemExit("[ERROR] crawl and fallback both returned empty data")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([asdict(r) for r in rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[DONE] saved {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
