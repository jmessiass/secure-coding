# ✅ Checklist de Segurança para Desenvolvedores

> **OWASP Top 10:2025 · Checklist prático para uso no dia a dia**
> Treinamento Desenvolvimento Seguro — Banco BTG · 2026

---

## 📋 A cada Pull Request

### Injeção (A05)
- [ ] Todas as queries SQL são parametrizadas (nenhum f-string/concat com input)
- [ ] Nenhum `os.system()` ou `subprocess.call()` com input do usuário sem sanitização
- [ ] Output é encoded/escaped antes de renderizar no HTML (prevenção XSS)

### Controle de Acesso (A01)
- [ ] Cada endpoint verifica `session["user_id"]` contra o recurso acessado
- [ ] Nenhum ID de recurso é confiado cegamente do request (anti-IDOR)
- [ ] Rotas administrativas exigem decorator/middleware de role check
- [ ] Não há SSRF: URLs externas são validadas contra whitelist

### Criptografia (A04)
- [ ] Senhas hasheadas com bcrypt/Argon2 (nunca MD5/SHA-1)
- [ ] Nenhum secret hardcoded no código (`secret_key`, API keys, senhas)
- [ ] Secrets vêm de vault ou variáveis de ambiente seguras
- [ ] Dados sensíveis em trânsito usam TLS 1.2+

### Autenticação (A07)
- [ ] Login tem rate limiting (máx 5 tentativas/minuto)
- [ ] Session é regenerada após login bem-sucedido
- [ ] Logout invalida a session no servidor

### Tratamento de Erros (A10)
- [ ] Exceções não expõem stack traces ao usuário
- [ ] Erros retornam mensagens genéricas + log detalhado no backend
- [ ] Transações parciais fazem rollback completo
- [ ] O sistema "fail closed" — nega acesso quando há dúvida

---

## 📋 A cada Sprint / Release

### Configuração (A02)
- [ ] `DEBUG = False` em produção
- [ ] Headers de segurança configurados (CSP, HSTS, X-Frame-Options)
- [ ] Endpoints de debug/test removidos ou protegidos
- [ ] Credenciais padrão removidas
- [ ] CORS configurado com origens específicas (não `*`)

### Supply Chain (A03)
- [ ] `pip audit` / `npm audit` executado sem vulnerabilidades críticas
- [ ] Dependências com versão fixa no lockfile
- [ ] Nenhuma dependência com CVE conhecida High/Critical
- [ ] SBOM atualizado (Software Bill of Materials)

### Design Seguro (A06)
- [ ] Limites de taxa em operações financeiras/sensíveis
- [ ] Velocity checks em transações (valor e frequência)
- [ ] Threat model revisado para novas funcionalidades

### Integridade (A08)
- [ ] Validação de entrada no servidor (não só no front-end)
- [ ] Pipelines CI/CD com separação de duties
- [ ] Artefatos de build assinados e verificados

### Logging e Alertas (A09)
- [ ] Eventos de segurança logados: login falho, IDOR, SSRF, erros
- [ ] Logs NÃO contêm PII (senhas, CPF, cartão)
- [ ] Alertas automáticos configurados para anomalias
- [ ] Logs centralizados e monitorados

---

## 📋 Antes do Deploy em Produção

### Segurança Geral
- [ ] SAST (análise estática) executado — 0 findings High/Critical
- [ ] DAST (análise dinâmica) executado — 0 findings High/Critical
- [ ] SCA (análise de composição) executado — 0 findings Critical
- [ ] Secrets scanning — 0 segredos no repositório
- [ ] Pentest executado (para releases críticas)

### Compliance
- [ ] Privacy by design aplicado (LGPD)
- [ ] Dados mínimos coletados (data minimization)
- [ ] Retention policy definida para logs e dados
- [ ] Segurança documentada no ADR (Architecture Decision Record)

---

## 📋 Pós-Incidente (Lessons Learned)

- [ ] Root cause identificado e documentado
- [ ] Correlação com OWASP Top 10 categoria
- [ ] Fix aplicado e testado
- [ ] Indicadores de comprometimento (IOCs) compartilhados
- [ ] Runbook atualizado
- [ ] Equipe notificada e treinamento atualizado se necessário

---

## 🔧 Comandos Úteis do Dia a Dia

```bash
# Scan de dependências vulneráveis
pip audit                                    # Python
npm audit                                    # Node.js
trivy fs --severity CRITICAL,HIGH .          # Multi-linguagem

# Buscar secrets no código
git log --all -p | grep -iE "password|secret|api_key|token"
gitleaks detect --source .

# Verificar headers de segurança
curl -sI https://sua-app.com | grep -iE "content-security|x-frame|strict-transport|x-content-type"

# SAST rápido
bandit -r . -ll                              # Python
semgrep --config auto .                      # Multi-linguagem

# Teste de SQL Injection básico
sqlmap -u "https://app.com/search?q=test" --batch --level 3
```

---

## 🚦 Severidade — Como Priorizar

| Criticidade | Ação | Exemplo |
|-------------|------|---------|
| 🔴 **Critical** | Fix imediato, bloqueia release | SQLi, RCE, secret exposto |
| 🟠 **High** | Fix antes do próximo deploy | IDOR, auth bypass, XSS armazenado |
| 🟡 **Medium** | Fix no sprint corrente | Missing headers, rate limit ausente |
| 🟢 **Low** | Backlog, próxima oportunidade | Verbose errors, outdated dependency |

---

> *Segurança é esporte coletivo — cada PR seguro fortalece toda a organização.*
