#!/usr/bin/python3

import sqlite3
import sys


def get_tables(cursor):
    fetch = cursor.execute("SELECT name FROM sqlite_master").fetchall()
    return [table[0] for table in fetch]


def get_columns(cursor, table):
    fetch = cursor.execute(f'SELECT * FROM {table} LIMIT 0')
    columns = [col[0] for col in fetch.description]
    return columns


def get_rows(cursor, table, columns):
    cols = ', '.join(columns)
    rows = cursor.execute(f'SELECT {cols} FROM {table}').fetchall()
    return rows


def gen_insert(table, columns, row):
    cols = ', '.join(columns)
    data = []
    for r in row:
        res = ''
        if isinstance(r, str):
            res = r.replace("'", "''")
        else:
            res = str(r)
        res = f'\'{res}\''
        data.append(res)
    statement = f'INSERT INTO {table}({cols}) VALUES({", ".join(data)});'
    return statement


if __name__ == '__main__':
    if len(sys.argv) > 2:
        db = sys.argv[1]
        dumpfile = sys.argv[2]
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        tables = get_tables(cur)
        lines = ''
        for table in tables:
            columns = get_columns(cur, table)
            rows = get_rows(cur, table, columns)
            for row in rows:
                line = gen_insert(table, columns, row)
                lines += line + '\n'
        with open(dumpfile, 'wt') as dump:
            dump.write(lines)




