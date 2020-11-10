from __future__ import annotations
from typing import*

import os

import sqlite3


db_path = os.environ.get("DB_PATH")
conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
cursor = conn.cursor()


def insert(amount: str) -> None:
    cursor.execute("insert into expense(amount) values (?)", (amount,))
    conn.commit()


def fetchall() -> List[Dict]:
    cursor.execute("SELECT * FROM expense")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {
            "amount": row[1],
            "created_at": row[2],
        }
        result.append(dict_row)
    return result


def get_all_sum() -> float:
    cursor.execute("SELECT SUM(amount) FROM expense")
    row = cursor.fetchone()
    return row[0]


def get_sum_by_days() -> Dict[str, float]:
    cursor.execute("SELECT DATE(created_at) as date, SUM(amount) as amount FROM expense GROUP BY date")
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        dt = row[0]
        result[dt] = row[1]
    return result


def get_date_range() -> Tuple[str, str]:
    cursor.execute("SELECT MIN(DATE(created_at)) as min_date, MAX(DATE(created_at)) as max_date FROM expense")
    row = cursor.fetchone()
    return row


def get_cursor():
    return cursor


def get_conn():
    return conn


def init() -> None: 
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def exists() -> bool:
    cursor.execute("SELECT name FROM sqlite_master "
               "WHERE type='table' AND name='expense'")
    table_exists = cursor.fetchall()
    if table_exists:
        return True
    return False

