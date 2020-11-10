import csv

import sqlite3

import db


if __name__ == "__main__":
    if not db.exists():
        db.init()
    conn = db.get_conn()
    cursor = db.get_cursor()
    with open("history.csv", "r") as f:
        rdr = csv.reader(f)
        for dt, amount in rdr:
            cursor.execute("insert into expense(amount, created_at) values (?,?)", (amount, dt))
    conn.commit()

