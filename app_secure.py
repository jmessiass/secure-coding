"""
VulnBank — Versão SEGURA
Mesma aplicação bancária com as correções aplicadas para cada vulnerabilidade.
Compare com app_vulnerable.py para ver as diferenças.
"""

import ipaddress
import logging
import os
import secrets
import sqlite3
from functools import wraps
from urllib.parse import urlparse

import bcrypt
from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ──────────────────────────────────────────────
# FIX A05: Secret key gerada de forma segura
# ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# FIX A05: Debug DESABILITADO
app.config["DEBUG"] = False

# FIX A05: Cookie seguro
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DATABASE = "vulnbank_secure.db"

# ──────────────────────────────────────────────
# FIX A09: Logging configurado
# ──────────────────────────────────────────────
logging.basicConfig(
    filename="security.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("vulnbank")

# ──────────────────────────────────────────────
# FIX A07: Rate limiting
# ──────────────────────────────────────────────
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"],
)


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
# FIX A05: Headers de segurança
# ──────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "script-src 'self' https://cdn.jsdelivr.net"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ──────────────────────────────────────────────
# Auth helpers
# ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            logger.warning(
                "Acesso admin negado para user_id=%s path=%s",
                session.get("user_id"),
                request.path,
            )
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
# FIX A05: Rota /debug REMOVIDA
# ──────────────────────────────────────────────
# (não existe na versão segura)


# ──────────────────────────────────────────────
# FIX A03 + A07 + A02: Login seguro
# ──────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # FIX A07: Rate limit no login
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        db = get_db()
        # FIX A03: Query parametrizada
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and bcrypt.checkpw(
            password.encode(), user["password"].encode()
        ):
            # FIX A07: Regenerar session
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            # FIX A09: Log de login bem-sucedido
            logger.info("Login bem-sucedido: user=%s ip=%s", username, request.remote_addr)
            return redirect(url_for("dashboard"))
        else:
            # FIX A09: Log de tentativa falha
            logger.warning(
                "Login falhou: user=%s ip=%s", username, request.remote_addr
            )
            error = "Credenciais inválidas"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    if "username" in session:
        logger.info("Logout: user=%s", session["username"])
    session.clear()
    return redirect(url_for("login"))


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────
@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    accounts = db.execute(
        "SELECT * FROM accounts WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    return render_template(
        "dashboard.html", username=session["username"], accounts=accounts
    )


# ──────────────────────────────────────────────
# FIX A01: Controle de acesso na visualização de contas
# ──────────────────────────────────────────────
@app.route("/account/<int:account_id>")
@login_required
def account_detail(account_id):
    db = get_db()
    # FIX A01: Verifica se a conta pertence ao usuário logado
    account = db.execute(
        "SELECT * FROM accounts WHERE id = ? AND user_id = ?",
        (account_id, session["user_id"]),
    ).fetchone()

    if not account:
        logger.warning(
            "IDOR attempt: user_id=%s tried account_id=%s",
            session["user_id"],
            account_id,
        )
        abort(403)

    transactions = db.execute(
        "SELECT * FROM transactions WHERE from_account = ? OR to_account = ? "
        "ORDER BY created_at DESC",
        (account_id, account_id),
    ).fetchall()

    return render_template(
        "account.html", account=account, transactions=transactions
    )


# ──────────────────────────────────────────────
# FIX A03 + A08: Transferência segura
# ──────────────────────────────────────────────
@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    db = get_db()
    accounts = db.execute(
        "SELECT * FROM accounts WHERE user_id = ?", (session["user_id"],)
    ).fetchall()

    message = None
    error = None

    if request.method == "POST":
        from_account = request.form.get("from_account", "")
        to_account = request.form.get("to_account", "")
        amount_str = request.form.get("amount", "")

        # FIX A08: Validação server-side rigorosa
        try:
            amount = float(amount_str)
            if amount <= 0 or amount > 1_000_000:
                raise ValueError("Valor inválido")
        except (ValueError, TypeError):
            error = "Valor inválido. Deve ser um número positivo até R$ 1.000.000."
            return render_template(
                "transfer.html", accounts=accounts, message=message, error=error
            )

        # FIX A01: Verifica se a conta origem pertence ao usuário
        source = db.execute(
            "SELECT * FROM accounts WHERE id = ? AND user_id = ?",
            (from_account, session["user_id"]),
        ).fetchone()

        if not source:
            error = "Conta origem inválida"
        elif source["balance"] < amount:
            error = "Saldo insuficiente"
        else:
            # FIX A03: Query parametrizada
            dest = db.execute(
                "SELECT * FROM accounts WHERE account_number = ?",
                (to_account,),
            ).fetchone()

            if dest:
                db.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                    (amount, source["id"]),
                )
                db.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                    (amount, dest["id"]),
                )
                db.execute(
                    "INSERT INTO transactions (from_account, to_account, amount) "
                    "VALUES (?, ?, ?)",
                    (source["id"], dest["id"], amount),
                )
                db.commit()
                # FIX A09: Log da transação
                logger.info(
                    "Transfer: user=%s from=%s to=%s amount=%.2f",
                    session["username"],
                    source["id"],
                    dest["id"],
                    amount,
                )
                message = f"Transferência de R$ {amount:.2f} realizada com sucesso!"
            else:
                error = "Conta destino não encontrada"

    return render_template(
        "transfer.html", accounts=accounts, message=message, error=error
    )


# ──────────────────────────────────────────────
# FIX A10: SSRF com whitelist
# ──────────────────────────────────────────────
ALLOWED_DOMAINS = {"api.exchangerate-api.com", "api.bcb.gov.br"}


def is_safe_url(url_string):
    """Valida se a URL é segura (não aponta para rede interna)."""
    try:
        parsed = urlparse(url_string)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Bloquear IPs internos
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            pass  # É um hostname, não IP
        # Whitelist de domínios permitidos
        if hostname not in ALLOWED_DOMAINS:
            return False
        return True
    except Exception:
        return False


@app.route("/fetch-url")
@login_required
def fetch_url():
    """Busca conteúdo de uma URL — com validação de destino."""
    import urllib.request

    url = request.args.get("url", "")
    content = ""
    error = None

    if url:
        # FIX A10: Validação da URL
        if not is_safe_url(url):
            logger.warning(
                "SSRF blocked: user=%s url=%s ip=%s",
                session.get("username"),
                url,
                request.remote_addr,
            )
            error = "URL não permitida. Apenas domínios autorizados."
        else:
            try:
                req = urllib.request.urlopen(url, timeout=5)
                content = req.read(10240).decode("utf-8", errors="replace")
            except Exception:
                error = "Não foi possível acessar a URL."

    return render_template("fetch.html", url=url, content=content, error=error)


# ──────────────────────────────────────────────
# FIX A01: Painel admin com controle de acesso
# ──────────────────────────────────────────────
@app.route("/admin/users")
@admin_required
def admin_users():
    db = get_db()
    # FIX A02: Não expõe hashes de senha
    users = db.execute("SELECT id, username, role FROM users").fetchall()
    return render_template("admin.html", users=users)


if __name__ == "__main__":
    # FIX A05: Bind em localhost, debug desabilitado
    app.run(host="127.0.0.1", port=5001, debug=False)
