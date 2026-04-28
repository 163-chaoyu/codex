#!/usr/bin/env python3
"""抓取南京小区房价并保存为 JSON。

默认从链家南京二手房小区列表页读取每个小区的名称、区域和均价。
如果页面结构变化，调整 SELECTORS 常量即可。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://nj.lianjia.com/xiaoqu/pg{page}/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

SELECTORS = {
    "item": "li.clear.xiaoquListItem",
    "name": "div.title a",
    "district": "div.positionInfo a.district",
    "price": "div.xiaoquListItemPrice span",
}


@dataclass
class CommunityPrice:
    communityName: str
    district: str
    avgUnitPrice: int
    source: str
    crawlDate: str


def parse_price(raw: str) -> int:
    digits = re.findall(r"\d+", raw)
    return int(digits[0]) if digits else 0


def crawl(max_pages: int, sleep_max: float) -> list[CommunityPrice]:
    crawl_date = dt.date.today().isoformat()
    output: list[CommunityPrice] = []

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page=page)
        print(f"[INFO] crawling page {page}: {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(SELECTORS["item"])
        if not cards:
            print("[WARN] no cards found, stop paging")
            break

        for card in cards:
            name_node = card.select_one(SELECTORS["name"])
            district_node = card.select_one(SELECTORS["district"])
            price_node = card.select_one(SELECTORS["price"])

            if not name_node or not price_node:
                continue

            output.append(
                CommunityPrice(
                    communityName=name_node.get_text(strip=True),
                    district=district_node.get_text(strip=True) if district_node else "未知",
                    avgUnitPrice=parse_price(price_node.get_text(strip=True)),
                    source="https://nj.lianjia.com",
                    crawlDate=crawl_date,
                )
            )

        time.sleep(random.uniform(0.5, sleep_max))

    output = [item for item in output if item.avgUnitPrice > 0]
    output.sort(key=lambda x: x.avgUnitPrice, reverse=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取南京小区房价")
    parser.add_argument("--max-pages", type=int, default=2, help="抓取页数")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("src/main/resources/data/nanjing_prices.json"),
        help="输出 JSON 文件路径",
    )
    parser.add_argument("--sleep-max", type=float, default=1.3, help="每页抓取后的随机等待上限（秒）")
    args = parser.parse_args()

    rows = crawl(max_pages=args.max_pages, sleep_max=args.sleep_max)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([asdict(r) for r in rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[DONE] saved {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
