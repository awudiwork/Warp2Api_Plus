#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('warp_accounts.db')
cursor = conn.cursor()

print("=== 表结构 ===")
cursor.execute('PRAGMA table_info(accounts)')
for row in cursor.fetchall():
    print(row)

print("\n=== 账号数量 ===")
cursor.execute('SELECT COUNT(*) FROM accounts')
print(f"总账号数: {cursor.fetchone()[0]}")

conn.close()
