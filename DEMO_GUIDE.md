# Guia de Demonstração — VulnBank

Guia passo-a-passo para o instrutor demonstrar cada vulnerabilidade durante o treinamento.

> **Setup antes do treinamento:**
> ```bash
> cd vuln-bank-demo
> python3 -m venv venv && source venv/bin/activate
> pip install -r requirements.txt
> python seed_db.py
> ```
> Abrir dois terminais: um para a versão vulnerável, outro para a segura.

---

## Demo 1 — SQL Injection no Login (A05:2025)

**Tempo estimado:** 3 minutos

### Versão Vulnerável (porta 5555)
```bash
python app_vulnerable.py
```

1. Abrir http://localhost:5555/login
2. No campo **Usuário**, digitar:
   ```
   ' OR 1=1 --
   ```
3. No campo **Senha**, digitar qualquer coisa
4. **Resultado:** Login como o primeiro usuário do banco (admin)

### Mostrar o código vulnerável
```python
# app_vulnerable.py — linha ~73
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password_hash}'"
```

A query montada fica:
```sql
SELECT * FROM users WHERE username = '' OR 1=1 --' AND password = '...'
```

### Versão Segura (porta 5001)
```bash
python app_secure.py
```
1. Tentar o mesmo payload — **resultado:** "Credenciais inválidas"
2. Mostrar o código corrigido:
```python
# app_secure.py — query parametrizada
user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
```

**Ponto-chave:** Queries parametrizadas eliminam 100% dos SQLi.

---

## Demo 2 — IDOR / Broken Access Control (A01:2025)

**Tempo estimado:** 2 minutos

### Versão Vulnerável
1. Fazer login como `joao` / `senha123`
2. Acessar `/account/1` (conta do admin) — **funciona!**
3. Acessar `/account/5` (conta da Maria) — **funciona!**

### Versão Segura
1. Login como `joao` / `senha123`
2. Acessar `/account/1` — **403 Forbidden**
3. Mostrar o código:
```python
# Vulnerável: não verifica dono
account = db.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()

# Seguro: filtra por user_id
account = db.execute(
    "SELECT * FROM accounts WHERE id = ? AND user_id = ?",
    (account_id, session["user_id"])
).fetchone()
```

**Ponto-chave:** Sempre validar ownership no backend, nunca confiar no client.

---

## Demo 3 — Security Misconfiguration (A02:2025)

**Tempo estimado:** 3 minutos

### 3a. Debug info exposta
1. Acessar http://localhost:5555/debug
2. Mostrar: secret key, variáveis de ambiente, config do app
3. Na versão segura: **rota não existe** (404)

### 3b. Headers de segurança ausentes
```bash
# Versão vulnerável
curl -I http://localhost:5555/login

# Versão segura
curl -I http://localhost:5001/login
```

Comparar os headers:
| Header | Vulnerável | Seguro |
|--------|-----------|--------|
| X-Content-Type-Options | ❌ ausente | ✅ nosniff |
| X-Frame-Options | ❌ ausente | ✅ DENY |
| Strict-Transport-Security | ❌ ausente | ✅ max-age=31536000 |
| Content-Security-Policy | ❌ ausente | ✅ default-src 'self' |

**Ponto-chave:** Usar ferramenta como https://securityheaders.com para validar.

---

## Demo 4 — Falha Criptográfica (A04:2025)

**Tempo estimado:** 2 minutos

### Versão Vulnerável
1. Login como `joao` (ou qualquer usuário)
2. Acessar `/admin/users`
3. Mostrar os hashes MD5 expostos
4. Copiar o hash do admin e buscar em https://crackstation.net
   - Hash: `0192023a7bbd73250516f069df18b500` → **admin123**

### Versão Segura
1. `/admin/users` retorna **403** (não é admin)
2. Mesmo como admin, hashes não são exibidos
3. Mostrar que usa bcrypt ao invés de MD5

**Ponto-chave:** MD5/SHA1 NÃO são funções de hash de senha. Usar bcrypt/Argon2/scrypt.

---

## Demo 5 — SSRF (A01:2025 — absorvido em Broken Access Control)

**Tempo estimado:** 3 minutos

### Versão Vulnerável
1. Acessar http://localhost:5555/fetch-url
2. Testar URLs maliciosas:
   ```
   http://localhost:5555/debug
   http://127.0.0.1:5555/admin/users
   ```
3. **Resultado:** Retorna conteúdo de rotas internas

### Versão Segura
1. Tentar as mesmas URLs
2. **Resultado:** "URL não permitida. Apenas domínios autorizados."
3. Mostrar a validação:
```python
ALLOWED_DOMAINS = {"api.exchangerate-api.com", "api.bcb.gov.br"}

def is_safe_url(url_string):
    # Bloqueia IPs privados, loopback, link-local
    # Só permite domínios da whitelist
```

**Ponto-chave:** Nunca permitir que o usuário controle URLs de requests server-side sem whitelist.

---

## Demo 6 — Falhas de Autenticação (A07:2025)

**Tempo estimado:** 2 minutos

### Versão Vulnerável
Mostrar no código:
- ❌ Sem rate limit — brute force livre
- ❌ Session fixation (não regenera sessão após login)
- ❌ Secret key hardcoded

### Versão Segura
Mostrar:
- ✅ `@limiter.limit("5 per minute")` no login
- ✅ `session.clear()` antes de popular a sessão
- ✅ Secret key via `secrets.token_hex(32)` ou env var
- ✅ Cookies com `httponly`, `samesite`

Demonstrar o rate limit:
```bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST \
    -d "username=admin&password=wrong" \
    http://localhost:5001/login
done
# Após 5 tentativas: 429 Too Many Requests
```

---

## Demo 7 — Logging / Alerta (A09:2025)

**Tempo estimado:** 1 minuto

### Versão Vulnerável
- Mostrar que não existe arquivo de log
- Falhas de login são silenciosas

### Versão Segura
1. Fazer algumas tentativas de login erradas
2. Tentar um IDOR
3. Tentar um SSRF
```bash
cat security.log
```
Saída esperada:
```
2026-03-29 10:15:01 [WARNING] Login falhou: user=hacker ip=127.0.0.1
2026-03-29 10:15:05 [WARNING] IDOR attempt: user_id=2 tried account_id=1
2026-03-29 10:15:10 [WARNING] SSRF blocked: user=joao url=http://localhost:5001/debug ip=127.0.0.1
2026-03-29 10:15:15 [INFO] Login bem-sucedido: user=admin ip=127.0.0.1
```

**Ponto-chave:** Se não tem log, você não sabe que está sendo atacado.

---

## Resumo — Lado a Lado

| Vuln (2025) | Vulnerável | Seguro |
|------|-----------|--------|
| A01 (Access Control + SSRF) | IDOR livre; SSRF sem restrição | Validação de ownership; Whitelist + validação de IP |
| A02 (Misconfiguration) | /debug, sem headers, debug=True | Rota removida, headers, debug=False |
| A04 (Crypto) | MD5, hashes expostos | bcrypt, dados ocultos |
| A05 (Injection) | String concat em SQL | Queries parametrizadas |
| A07 (Auth) | Sem rate limit, session fixation | Rate limit, session regeneration |
| A08 (Integrity) | Sem validação server-side | Validação rigorosa de input |
| A09 (Logging & Alerting) | Sem logs | Logging estruturado |
| A10 (Exceptional Conditions) | Stack trace exposta, failing open | Error handling centralizado, fail closed |

---

