"""
VulnBank — Versão VULNERÁVEL
Aplicação bancária com vulnerabilidades intencionais do OWASP Top 10.
⚠️  NUNCA use este código em produção.
"""

import hashlib
import os
import sqlite3
import urllib.request

from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "chave-super-secreta-123"  # A05: Hardcoded secret

# A05: Debug habilitado
app.config["DEBUG"] = True

DATABASE = "vulnbank.db"


# ──────────────────────────────────────────────
# Database helpers
# ──────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ──────────────────────────────────────────────
# A05: Debug route expondo informações internas
# ──────────────────────────────────────────────
@app.route("/debug")
def debug_info():
    """Expõe informações sensíveis do ambiente — Security Misconfiguration."""
    env_vars = {k: v for k, v in os.environ.items()}
    return jsonify(
        {
            "app_config": {k: str(v) for k, v in app.config.items()},
            "environment": env_vars,
            "database": DATABASE,
            "secret_key": app.secret_key,
        }
    )


# ──────────────────────────────────────────────
# A03 + A07: Login com SQL Injection e sem rate limit
# ──────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # A02: Hash fraco (MD5)
        password_hash = hashlib.md5(password.encode()).hexdigest()

        # A03: SQL Injection — concatenação direta
        db = get_db()
        query = (
            f"SELECT * FROM users WHERE username = '{username}' "
            f"AND password = '{password_hash}'"
        )
        # A09: Sem log de tentativa de login
        try:
            user = db.execute(query).fetchone()
        except Exception:
            user = None

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            # A07: Session fixation — não regenera session ID
            return redirect(url_for("dashboard"))
        else:
            error = "Credenciais inválidas"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────
@app.route("/")
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    accounts = db.execute(
        "SELECT * FROM accounts WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    return render_template(
        "dashboard.html", username=session["username"], accounts=accounts
    )


# ──────────────────────────────────────────────
# A01: IDOR — Broken Access Control
# ──────────────────────────────────────────────
@app.route("/account/<int:account_id>")
def account_detail(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    # A01: Não verifica se a conta pertence ao usuário logado
    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?", (account_id,)
    ).fetchone()

    if not account:
        return "Conta não encontrada", 404

    transactions = db.execute(
        "SELECT * FROM transactions WHERE from_account = ? OR to_account = ? "
        "ORDER BY created_at DESC",
        (account_id, account_id),
    ).fetchall()

    return render_template(
        "account.html", account=account, transactions=transactions
    )


# ──────────────────────────────────────────────
# A03 + A08: Transferência com SQL Injection e sem validação de integridade
# ──────────────────────────────────────────────
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    accounts = db.execute(
        "SELECT * FROM accounts WHERE user_id = ?", (session["user_id"],)
    ).fetchall()

    message = None
    error = None

    if request.method == "POST":
        from_account = request.form["from_account"]
        to_account = request.form["to_account"]
        amount = request.form["amount"]

        # A08: Sem validação server-side do valor (confia no client)
        # A03: SQL Injection no campo to_account
        try:
            query = (
                f"SELECT * FROM accounts WHERE account_number = '{to_account}'"
            )
            dest = db.execute(query).fetchone()

            if dest:
                # Debita da conta origem
                db.execute(
                    f"UPDATE accounts SET balance = balance - {amount} "
                    f"WHERE id = {from_account}"
                )
                # Credita na conta destino
                db.execute(
                    f"UPDATE accounts SET balance = balance + {amount} "
                    f"WHERE id = {dest['id']}"
                )
                # Registra transação
                db.execute(
                    "INSERT INTO transactions (from_account, to_account, amount) "
                    "VALUES (?, ?, ?)",
                    (from_account, dest["id"], amount),
                )
                db.commit()
                # A09: Sem log da transação
                message = f"Transferência de R$ {amount} realizada com sucesso!"
            else:
                error = "Conta destino não encontrada"
        except Exception as e:
            error = f"Erro: {e}"  # A05: Expondo stack trace

    return render_template(
        "transfer.html", accounts=accounts, message=message, error=error
    )


# ──────────────────────────────────────────────
# A10: SSRF — Server-Side Request Forgery
# ──────────────────────────────────────────────
@app.route("/fetch-url")
def fetch_url():
    """Busca conteúdo de uma URL — sem validação do destino."""
    url = request.args.get("url", "")
    content = ""
    error = None

    if url:
        try:
            # A10: Nenhuma validação/whitelist da URL
            req = urllib.request.urlopen(url, timeout=5)
            content = req.read().decode("utf-8", errors="replace")
        except Exception as e:
            error = str(e)

    return render_template("fetch.html", url=url, content=content, error=error)


# ──────────────────────────────────────────────
# A01 + A05: Painel admin sem controle de acesso adequado
# ──────────────────────────────────────────────
@app.route("/admin")
def admin_index():
    return redirect(url_for("admin_users"))


@app.route("/admin/users")
def admin_users():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # A01: Não verifica se o usuário é admin
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    # A02: Exibe hashes de senha na interface
    return render_template("admin.html", users=users)


# ──────────────────────────────────────────────
# A05: Headers de segurança ausentes (sem CSP, HSTS, etc.)
# ──────────────────────────────────────────────
# Nenhum middleware de headers de segurança configurado.


if __name__ == "__main__":
    # A05: Rodando em 0.0.0.0 com debug
    app.run(host="0.0.0.0", port=5555, debug=True)
