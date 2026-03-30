# 🏦 VulnBank — Lab de Desenvolvimento Seguro

Aplicação bancária propositalmente vulnerável para demonstração prática das vulnerabilidades do **OWASP Top 10:2025** durante treinamentos de desenvolvimento seguro.

Cada vulnerabilidade possui uma versão **vulnerável** e uma **segura**, permitindo comparação lado a lado em tempo real.

> ⚠️ **ATENÇÃO:** Esta aplicação contém vulnerabilidades **INTENCIONAIS** para fins educacionais. **NUNCA** use este código em produção ou exponha em rede pública.

---

## Início Rápido

### Opção 1: Python local

```bash
git clone https://github.com/jmessiass/secure-coding.git
cd secure-coding

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Popular o banco de dados com dados de teste
python seed_db.py

# Terminal 1 — versão VULNERÁVEL (porta 5555)
python app_vulnerable.py

# Terminal 2 — versão SEGURA (porta 5001)
python app_secure.py
```

### Opção 2: Docker

```bash
# Versão vulnerável (porta 5555)
docker build -t vulnbank-vuln -f Dockerfile.vulnerable .
docker run -p 5555:5555 vulnbank-vuln

# Versão segura (porta 5001)
docker build -t vulnbank-secure -f Dockerfile.secure .
docker run -p 5001:5001 vulnbank-secure
```

### Acesso

| Versão | URL | Porta |
|--------|-----|-------|
| Vulnerável | http://localhost:5555 | 5555 |
| Segura | http://localhost:5001 | 5001 |

**Usuários de teste** (criados pelo `seed_db.py`):

| Usuário | Senha |
|---------|-------|
| `admin` | `admin123` |
| `joao` | `senha123` |
| `maria` | `senha456` |

---

## Vulnerabilidades Demonstráveis (OWASP Top 10:2025)

| # | OWASP 2025 | Vulnerabilidade | Rota | Exploração |
|---|------------|-----------------|------|------------|
| 1 | **A01** Quebra de Controle de Acesso | IDOR | `/account/<id>` | Trocar o ID na URL para ver conta de outro usuário |
| 2 | **A01** Quebra de Controle de Acesso | SSRF | `/fetch-url` | `?url=http://169.254.169.254/latest/meta-data/` |
| 3 | **A02** Configuração Incorreta | Debug info exposta | `/debug` | Acessar endpoint com informações do sistema |
| 4 | **A02** Configuração Incorreta | Headers ausentes | `curl -I` | `curl -I http://localhost:5555` — sem CSP, HSTS, X-Frame |
| 5 | **A04** Falhas Criptográficas | MD5 para senhas | `/admin/users` | Hashes MD5 reversíveis no banco de dados |
| 6 | **A05** Injeção | SQL Injection (login) | `/login` | `' OR 1=1 --` no campo usuário |
| 7 | **A05** Injeção | SQL Injection (transferência) | `/transfer` | Injetar SQL no campo de conta destino |
| 8 | **A07** Falhas de Autenticação | Brute force / Session fixation | `/login` | Sem rate limit, sem regeneração de session |
| 9 | **A09** Falhas de Registro e Alerta | Logging ausente | Todos | Nenhum log de segurança, falhas silenciosas |
| 10 | **A10** Condições Excepcionais | Stack trace exposto | Erros | Mensagens de erro detalhadas para o usuário |

> 📖 Para o passo a passo completo de cada exploit, veja o **[DEMO_GUIDE.md](DEMO_GUIDE.md)**.

---

## Comparação: Vulnerável vs. Seguro

| Aspecto | `app_vulnerable.py` | `app_secure.py` |
|---------|---------------------|-----------------|
| Queries SQL | Concatenação de strings | Parametrizadas (`?`) |
| Hash de senha | MD5 | bcrypt |
| Rate limiting | Nenhum | 5 req/min no login |
| Session | Sem regeneração | Regenerada pós-login |
| Secret key | Hardcoded | `secrets.token_hex(32)` |
| Headers HTTP | Ausentes | CSP, HSTS, X-Frame-Options |
| SSRF | Sem validação de URL | Whitelist de domínios |
| Logs | Nenhum | `security.log` estruturado |
| Erros | Stack trace exposto | Mensagem genérica + log interno |
| Debug | `debug=True` | `debug=False` |

---

## Estrutura do Projeto

```
vuln-bank-demo/
├── app_vulnerable.py       # 🔴 App com vulnerabilidades intencionais (porta 5555)
├── app_secure.py            # 🟢 App com correções aplicadas (porta 5001)
├── seed_db.py               # Popular banco de dados com dados de teste
├── requirements.txt         # flask, bcrypt, flask-limiter
├── DEMO_GUIDE.md            # Guia passo a passo de cada exploit
├── Dockerfile.vulnerable
├── Dockerfile.secure
├── templates/
│   ├── login.html           # Tela de login
│   ├── dashboard.html       # Painel principal
│   ├── account.html         # Detalhe da conta (IDOR demo)
│   ├── transfer.html        # Transferência bancária (SQLi demo)
│   ├── admin.html           # Painel admin (auth bypass demo)
│   └── fetch.html           # Consulta de URL (SSRF demo)
└── bonus/                   # Material bônus
    ├── README.md            # Índice dos materiais
    ├── 01-guia-de-bolso-seguranca.md   # Referência rápida OWASP Top 10:2025
    ├── 02-checklist-seguranca-dev.md   # Checklist por PR / sprint / release
    └── 03-prompts-ia-seguranca.md      # Prompts de IA para codificação segura
```

---

## Material Bônus

A pasta [`bonus/`](bonus/) contém materiais de apoio para os participantes do treinamento:

| Material | Descrição |
|----------|-----------|
| [Guia de Bolso](bonus/01-guia-de-bolso-seguranca.md) | Referência rápida: ✅/❌ por categoria OWASP 2025, código-chave, headers obrigatórios |
| [Checklist](bonus/02-checklist-seguranca-dev.md) | Checklists acionáveis por PR, sprint e release + comandos úteis |
| [Prompts de IA](bonus/03-prompts-ia-seguranca.md) | 10 prompts prontos para Copilot/ChatGPT para auditoria e geração de código seguro |

---

## Tecnologias

- **Backend:** Python 3.11+ / Flask 3.1
- **Banco de dados:** SQLite (arquivo local, zero config)
- **Frontend:** HTML + Bootstrap 5.3 (dark theme)
- **Segurança:** bcrypt 4.2, flask-limiter 3.8
- **Containers:** Docker (Dockerfiles incluídos)

---

## Referências

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP SAMM](https://owaspsamm.org/)
- [Security Headers Scanner](https://securityheaders.com/)

---

## Licença

Este projeto é destinado exclusivamente para **fins educacionais** em treinamentos de segurança de aplicações.

---

> *"O atacante só precisa de uma brecha; o desenvolvedor precisa fechar todas."*
