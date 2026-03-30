"""
Seed script — Cria e popula o banco de dados para ambas as versões.
Uso: python seed_db.py [vulnerable|secure|both]
"""

import hashlib
import sqlite3
import sys

import bcrypt


def create_schema(db):
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            account_type TEXT DEFAULT 'corrente',
            balance REAL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_account INTEGER,
            to_account INTEGER,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_account) REFERENCES accounts(id),
            FOREIGN KEY (to_account) REFERENCES accounts(id)
        );
    """)


def seed_vulnerable(db_path="vulnbank.db"):
    """Popula o banco da versão vulnerável com senhas em MD5."""
    db = sqlite3.connect(db_path)
    create_schema(db)

    users = [
        ("admin", hashlib.md5("admin123".encode()).hexdigest(), "admin"),
        ("joao", hashlib.md5("senha123".encode()).hexdigest(), "user"),
        ("maria", hashlib.md5("senha456".encode()).hexdigest(), "user"),
    ]

    for username, password, role in users:
        db.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role),
        )

    accounts = [
        (1, "100001", "corrente", 50000.00),
        (1, "100002", "poupanca", 120000.00),
        (2, "200001", "corrente", 8500.00),
        (2, "200002", "poupanca", 32000.00),
        (3, "300001", "corrente", 15000.00),
    ]

    for user_id, acc_num, acc_type, balance in accounts:
        db.execute(
            "INSERT OR IGNORE INTO accounts (user_id, account_number, account_type, balance) "
            "VALUES (?, ?, ?, ?)",
            (user_id, acc_num, acc_type, balance),
        )

    transactions = [
        (1, 3, 1500.00),
        (3, 1, 750.00),
        (2, 5, 200.00),
    ]

    for from_acc, to_acc, amount in transactions:
        db.execute(
            "INSERT INTO transactions (from_account, to_account, amount) VALUES (?, ?, ?)",
            (from_acc, to_acc, amount),
        )

    db.commit()
    db.close()
    print(f"[+] Banco vulnerável criado: {db_path}")
    print("    Senhas (MD5): admin123, senha123, senha456")


def seed_secure(db_path="vulnbank_secure.db"):
    """Popula o banco da versão segura com senhas em bcrypt."""
    db = sqlite3.connect(db_path)
    create_schema(db)

    users = [
        ("admin", bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(), "admin"),
        ("joao", bcrypt.hashpw("senha123".encode(), bcrypt.gensalt()).decode(), "user"),
        ("maria", bcrypt.hashpw("senha456".encode(), bcrypt.gensalt()).decode(), "user"),
    ]

    for username, password, role in users:
        db.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role),
        )

    accounts = [
        (1, "100001", "corrente", 50000.00),
        (1, "100002", "poupanca", 120000.00),
        (2, "200001", "corrente", 8500.00),
        (2, "200002", "poupanca", 32000.00),
        (3, "300001", "corrente", 15000.00),
    ]

    for user_id, acc_num, acc_type, balance in accounts:
        db.execute(
            "INSERT OR IGNORE INTO accounts (user_id, account_number, account_type, balance) "
            "VALUES (?, ?, ?, ?)",
            (user_id, acc_num, acc_type, balance),
        )

    transactions = [
        (1, 3, 1500.00),
        (3, 1, 750.00),
        (2, 5, 200.00),
    ]

    for from_acc, to_acc, amount in transactions:
        db.execute(
            "INSERT INTO transactions (from_account, to_account, amount) VALUES (?, ?, ?)",
            (from_acc, to_acc, amount),
        )

    db.commit()
    db.close()
    print(f"[+] Banco seguro criado: {db_path}")
    print("    Senhas (bcrypt): admin123, senha123, senha456")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "both"

    if target in ("vulnerable", "both"):
        seed_vulnerable()
    if target in ("secure", "both"):
        seed_secure()
    if target == "both":
        print("\n[✓] Ambos os bancos criados com sucesso!")
