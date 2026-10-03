"""Part 1 runner: executes every named query in queries.sql and saves CSVs."""
import csv
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "meesho_reseller.db")
OUT = os.path.join(HERE, "output")


def load_queries(path):
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.M)
    # parts = [preamble, name1, body1, name2, body2, ...]
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def main():
    os.makedirs(OUT, exist_ok=True)
    conn = sqlite3.connect(DB)
    for name, sql in load_queries(os.path.join(HERE, "queries.sql")).items():
        cur = conn.execute(sql)
        header = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(os.path.join(OUT, f"{name}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"{name}: {len(rows)} row(s) -> output/{name}.csv")
    conn.close()


if __name__ == "__main__":
    main()
