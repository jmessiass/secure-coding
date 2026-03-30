# 🛡️ Guia de Bolso — Desenvolvimento Seguro

> **OWASP Top 10:2025 · Referência rápida para desenvolvedores**
> Treinamento Desenvolvimento Seguro — Banco BTG · 2026

---

## A01 — Quebra de Controle de Acesso (+ SSRF)

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Validar ownership no backend              Confiar em IDs vindos do client
Deny-by-default em toda rota              Liberar acesso e restringir depois
Verificar role + user_id por request      Checar permissão só no front-end
Whitelist de URLs para requests server    Deixar o usuário controlar URLs de
                                          requisições internas (SSRF)
```

**Código‑chave:**
```python
# ✅ Seguro — verifica se o recurso pertence ao usuário
account = db.execute(
    "SELECT * FROM accounts WHERE id = ? AND user_id = ?",
    (account_id, session["user_id"])
).fetchone()
if not account:
    abort(403)
```

---

## A02 — Configuração Incorreta de Segurança

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Desabilitar debug em produção             Subir com DEBUG=True
Setar headers: CSP, HSTS, X-Frame        Ignorar headers de segurança
Remover rotas de admin/debug              Deixar /debug, /admin acessíveis
Credenciais únicas por ambiente           Compartilhar secrets entre envs
```

**Validação rápida:**
```bash
curl -I https://sua-app.com | grep -E "Content-Security|X-Frame|Strict-Transport"
```

---

## A03 — Falhas na Cadeia de Suprimentos (Supply Chain)

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Gerar e manter SBOM atualizado            Ignorar dependências transitivas
Rodar pip audit / npm audit semanalmente  Instalar pacotes sem verificar
Fixar versões no requirements/lockfile    Usar "latest" em produção
Assinar artefatos de build                Promover builds sem verificação
Auditar fornecedores terceiros            Confiar cegamente em integrações
```

**Caso real:** C&M Software (2025) → comprometeu BTG e desviou R$ 100–230M via Pix.

---

## A04 — Falhas Criptográficas

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
bcrypt/Argon2/scrypt para senhas          MD5, SHA-1 para hash de senha
TLS 1.2+ obrigatório                     HTTP em produção
Rotação automática de chaves              Hardcoded secrets no código
Vault (HashiCorp, AWS Secrets Manager)    Env vars em texto plano no repo
```

**Teste rápido:** Cole um hash MD5 no https://crackstation.net — se reverter, é fraco.

---

## A05 — Injeção (SQLi, XSS, Command Injection)

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Queries parametrizadas SEMPRE             Concatenar strings em SQL
Validar e sanitizar todo input            Confiar em dados do formulário
Usar ORM com prepared statements          Montar queries com f-strings
Encode output para prevenir XSS           Renderizar input cru no HTML
```

**Código‑chave:**
```python
# ❌ Vulnerável
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ Seguro
user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
```

---

## A06 — Design Inseguro

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Threat modeling antes de codar            Pensar em segurança só no deploy
Rate limit em endpoints críticos          Transferências ilimitadas
Velocity checks em transações             Ignorar volume/frequência atípica
Circuit breakers automáticos              Confiar que "ninguém vai abusar"
```

**Pergunta de design:** "E se alguém repetir isso 10.000 vezes em 1 minuto?"

---

## A07 — Falhas de Autenticação

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Rate limit no login (5/min)               Brute force sem bloqueio
Regenerar session após login              Session fixation
MFA em operações sensíveis                Apenas username/password
Secret key gerada com secrets.token_hex   Hardcoded: "chave-secreta-123"
mTLS entre serviços internos              Trust baseado só em rede interna
```

---

## A08 — Falhas de Integridade de Software e Dados

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Assinar builds e artefatos                Promover sem verificação
Validar input server-side                 Confiar em validação do front
Verificar integridade de downloads        Executar binários sem checksums
Separar duties no CI/CD                   Mesma pessoa commita e deploya
```

---

## A09 — Falhas de Registro e Alerta

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Logar: login falho, IDOR, SSRF, erros    Silenciar falhas de segurança
Configurar ALERTAS automáticos            Ter logs sem ninguém olhando
Incluir: timestamp, IP, user, ação        Logar PII (senhas, CPF, cartão)
Monitorar desvios de baseline             Alertar só quando já é tarde
```

**O que logar:**
```
2026-03-22 08:15:01 [WARNING] Login falhou: user=hacker ip=203.0.113.1
2026-03-22 08:15:05 [WARNING] IDOR attempt: user_id=2 tried account_id=1
2026-03-22 08:15:10 [WARNING] SSRF blocked: url=http://169.254.169.254
```

---

## A10 — Tratamento Inadequado de Condições Excepcionais (NOVO 2025)

```
✅ FAÇA                                  ❌ NÃO FAÇA
─────────────────────────────────────────────────────────────
Fail closed (nega na dúvida)              Fail open (permite na dúvida)
Rollback completo de transações parciais  Deixar transação pela metade
Error handler global + msgs genéricas     Stack trace para o usuário
Rate limit + resource quotas              Recursos ilimitados
Catch específico com tratamento           Catch genérico sem ação
```

**Código‑chave:**
```python
# ❌ Vulnerável — expõe stack trace
except Exception as e:
    return f"Erro: {e}"

# ✅ Seguro — mensagem genérica + log interno
except Exception as e:
    logger.error("Transfer error: %s", e)
    return "Erro ao processar transação. Tente novamente.", 500
```

---

## Quick Reference — Headers HTTP Obrigatórios

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
X-XSS-Protection: 1; mode=block
```

---

## Links Essenciais

| Recurso | Link |
|---------|------|
| OWASP Top 10:2025 | https://owasp.org/Top10/2025/ |
| OWASP Cheat Sheet Series | https://cheatsheetseries.owasp.org/ |
| OWASP SAMM | https://owaspsamm.org/ |
| Security Headers Scanner | https://securityheaders.com/ |
| CrackStation (hash lookup) | https://crackstation.net/ |
| CVE Database | https://www.cve.org/ |
| OWASP Top 10 for LLMs | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |

---

> *"O atacante só precisa de uma brecha; o desenvolvedor precisa fechar todas."*
