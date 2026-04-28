#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import sqlglot
    from sqlglot import exp
except ImportError:
    print("缺少依赖: sqlglot。请先安装: pip install sqlglot", file=sys.stderr)
    raise SystemExit(1)


def normalize_identifier(table: exp.Table) -> str:
    parts: list[str] = []
    if table.catalog:
        parts.append(table.catalog)
    if table.db:
        parts.append(table.db)
    if table.name:
        parts.append(table.name)
    return ".".join(parts)


def _collect_source_tables(node: exp.Expression, target: str | None = None) -> set[str]:
    sources: set[str] = set()
    for table in node.find_all(exp.Table):
        name = normalize_identifier(table)
        if not name:
            continue
        if target and name == target:
            continue
        sources.add(name)
    return sources


def extract_lineage(sql: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    statements = sqlglot.parse(sql)
    for stmt in statements:
        if isinstance(stmt, exp.Insert):
            target_table = stmt.this if isinstance(stmt.this, exp.Table) else stmt.this.find(exp.Table)
            if target_table is None:
                continue
            target = normalize_identifier(target_table)
            for source in _collect_source_tables(stmt.expression, target=target):
                pairs.add((source, target))

        elif isinstance(stmt, exp.Create):
            if not isinstance(stmt.this, exp.Table):
                continue
            target = normalize_identifier(stmt.this)
            if not target or stmt.expression is None:
                continue
            for source in _collect_source_tables(stmt.expression, target=target):
                pairs.add((source, target))

    return pairs


def main() -> int:
    if len(sys.argv) != 2:
        print(f"用法: {Path(sys.argv[0]).name} path/to/file.sql", file=sys.stderr)
        return 1

    sql_file = Path(sys.argv[1])
    if not sql_file.is_file():
        print(f"文件不存在: {sql_file}", file=sys.stderr)
        return 1

    sql = sql_file.read_text(encoding="utf-8", errors="ignore")
    lineage = sorted(extract_lineage(sql))
    for source, target in lineage:
        print(f"{source} -> {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
