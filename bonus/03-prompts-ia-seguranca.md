# 🤖 Prompts de IA para Codificação Segura

> **Copilot, ChatGPT, Claude & LLMs — Prompts prontos para copiar e usar**
> Treinamento Desenvolvimento Seguro — Banco BTG · 2026

---

## Como Usar

1. **Copie o prompt** na íntegra
2. **Cole o seu código** onde indicado `[SEU CÓDIGO AQUI]`
3. **Revise criticamente** — IA é co-piloto, você é o piloto
4. **Nunca cole código com secrets reais** em ferramentas externas

> ⚠️ **Alerta OWASP Top 10 para LLMs:** Não confie cegamente na resposta. Valide cada sugestão contra a checklist de segurança.

---

## 1. 🔍 Revisão de Segurança Geral

### Prompt: Auditoria Completa OWASP
```
Atue como um engenheiro de segurança de aplicações sênior.
Analise o código abaixo e identifique TODAS as vulnerabilidades
de segurança, classificando cada uma segundo o OWASP Top 10:2025:

- A01: Quebra de Controle de Acesso
- A02: Configuração Incorreta de Segurança
- A03: Falhas na Cadeia de Suprimentos
- A04: Falhas Criptográficas
- A05: Injeção
- A06: Design Inseguro
- A07: Falhas de Autenticação
- A08: Falhas de Integridade de Software e Dados
- A09: Falhas de Registro e Alerta
- A10: Tratamento Inadequado de Condições Excepcionais

Para cada vulnerabilidade encontrada, forneça:
1. Categoria OWASP (ex: A05 — Injeção)
2. Linha(s) afetada(s)
3. Severidade (Critical/High/Medium/Low)
4. Descrição do risco em 1 frase
5. Código corrigido (patch)

Código:
```
[SEU CÓDIGO AQUI]
```
```

---

## 2. 💉 Detecção de SQL Injection

### Prompt: Encontrar SQLi
```
Analise o código abaixo e identifique TODOS os pontos vulneráveis
a SQL Injection. Para cada ponto:

1. Mostre a linha vulnerável
2. Explique o vetor de ataque (payload de exemplo)
3. Mostre a correção usando queries parametrizadas
4. Confirme se a correção é segura contra second-order injection

Se usar ORM, verifique se há raw queries inseguras.
Se não encontrar vulnerabilidades, confirme explicitamente.

Código:
```
[SEU CÓDIGO AQUI]
```
```

---

## 3. 🔐 Revisão de Autenticação e Sessão

### Prompt: Auth & Session Security
```
Revise o código de autenticação abaixo e verifique:

1. Senhas estão sendo hasheadas com bcrypt/Argon2/scrypt?
   (MD5, SHA-1, SHA-256 sem salt NÃO são aceitáveis para senhas)
2. Há rate limiting no endpoint de login?
3. A session é regenerada após login bem-sucedido?
4. O logout invalida a session no servidor?
5. Há proteção contra session fixation?
6. Credenciais estão hardcoded no código?
7. A secret key é gerada com entropia suficiente?
   (ex: secrets.token_hex(32))
8. Há MFA disponível para operações sensíveis?

Para cada problema, dê o fix com código.

Código:
```
[SEU CÓDIGO AQUI]
```
```

---

## 4. 🛡️ Geração de Código Seguro

### Prompt: Gerar Endpoint Seguro
```
Gere um endpoint [TIPO: REST API / GraphQL / gRPC] em [LINGUAGEM]
para [DESCRIÇÃO DA FUNCIONALIDADE].

O endpoint DEVE incluir:
- Autenticação: verificar token/session do usuário
- Autorização: verificar se o usuário tem permissão no recurso (anti-IDOR)
- Validação de input: tipo, tamanho, formato, ranges
- Query parametrizada (nunca concatenar input em SQL)
- Rate limiting com limite configurável
- Logging de segurança: tentativas de acesso indevido
- Headers de segurança na resposta
- Error handling: mensagens genéricas para o client, detalhes no log
- Try/except com fail-closed (nega acesso na dúvida)

NÃO inclua:
- Debug mode
- Stack traces na resposta
- Hardcoded secrets
- Comentários com hints de vulnerabilidade
```

### Prompt: Gerar Transferência Bancária Segura
```
Gere uma função de transferência bancária em Python (Flask + SQLite)
que implemente TODAS as seguintes proteções:

1. Verificar que o usuário autenticado é dono da conta de origem
2. Validar valor: float positivo, máximo R$ 1.000.000
3. Verificar saldo suficiente
4. Transação atômica (BEGIN/COMMIT/ROLLBACK)
5. Rate limit: máximo 10 transferências por minuto
6. Log: registrar toda transferência (from, to, amount, timestamp, IP)
7. Mensagem de erro genérica se falhar
8. Retornar 403 se houver tentativa de acesso a conta alheia

Use queries parametrizadas e bcrypt para qualquer verificação de senha.
```

---

## 5. 🌐 Revisão de SSRF

### Prompt: Detectar SSRF
```
Analise o código abaixo e identifique se há vulnerabilidades de
Server-Side Request Forgery (SSRF).

Verifique:
1. O usuário pode controlar a URL de uma requisição server-side?
2. Há whitelist de domínios/IPs permitidos?
3. Endereços internos são bloqueados? (127.0.0.1, 169.254.169.254,
   10.x, 172.16-31.x, 192.168.x, localhost, metadata endpoints)
4. Há resolução DNS seguida de validação (anti DNS rebinding)?
5. O protocolo é restrito (apenas https)?

Para cada SSRF encontrado, mostre:
- O vetor de ataque (payload)
- O impacto (ex: acesso a metadata AWS, scan de rede interna)
- A correção com whitelist + validação

Código:
```
[SEU CÓDIGO AQUI]
```
```

---

## 6. 📦 Análise de Dependências

### Prompt: Avaliar Supply Chain Risk
```
Analise as dependências abaixo (requirements.txt / package.json)
e avalie:

1. Alguma dependência tem CVE conhecida? (verifique se
   as versões listadas são afetadas)
2. Há dependências não essenciais que aumentam a attack surface?
3. As versões estão fixadas (pinned) ou usam ranges abertos?
4. Há alternativas mais seguras/mantidas para alguma dependência?
5. Qual o nível de manutenção de cada pacote?
   (último commit, número de maintainers)

Dependências:
```
[SEU REQUIREMENTS.TXT / PACKAGE.JSON AQUI]
```
```

---

## 7. 🧪 Gerar Testes de Segurança

### Prompt: Testes Automatizados de Segurança
```
Gere testes de segurança (pytest/jest) para o endpoint abaixo.
Os testes devem cobrir:

1. SQL Injection: enviar payloads como ' OR 1=1 --, UNION SELECT
2. IDOR: acessar recurso de outro usuário
3. Auth bypass: acessar sem token/session
4. Rate limiting: exceder o limite e verificar 429
5. Input validation: valores negativos, zero, extremos, tipos errados
6. XSS: enviar <script>alert(1)</script> e verificar encoding
7. SSRF: enviar URLs internas (127.0.0.1, metadata)
8. Error handling: provocar exceção e verificar que não vaza stack trace

Cada teste deve ter nome descritivo (test_transfer_rejects_sqli_payload).
Use fixtures para setup de usuários autenticados.

Endpoint:
```
[SEU CÓDIGO AQUI]
```
```

---

## 8. 📊 Revisão de Logs e Alertas

### Prompt: Avaliar Logging de Segurança
```
Revise o código abaixo e avalie o logging de segurança:

1. Eventos que DEVEM ser logados (verificar presença):
   - Login bem-sucedido e falho (com IP e username)
   - Tentativa de acesso não autorizado (IDOR)
   - Requisições SSRF bloqueadas
   - Erros de validação de input
   - Transações financeiras
   - Alteração de permissões

2. Dados que NÃO devem ser logados:
   - Senhas (nem em hash)
   - Números de cartão completos
   - CPF/RG
   - Tokens de sessão
   - API keys

3. Formato do log é adequado? (timestamp, severity, user, IP, action)
4. Os logs são suficientes para investigar um incidente?
5. Há alertas automáticos para eventos críticos?

Código:
```
[SEU CÓDIGO AQUI]
```
```

---

## 9. 🏗️ Threat Modeling com IA

### Prompt: Threat Model de Feature
```
Atue como arquiteto de segurança. Faço o threat model da
seguinte funcionalidade usando STRIDE:

Funcionalidade: [DESCREVA A FEATURE]
Stack: [LINGUAGEM/FRAMEWORK/DB/INFRA]
Usuários: [QUEM USA — interno, externo, admin]

Para cada categoria STRIDE, identifique:
- Spoofing: como alguém pode se passar por outro?
- Tampering: como dados podem ser alterados indevidamente?
- Repudiation: como alguém pode negar uma ação?
- Information Disclosure: como dados podem vazar?
- Denial of Service: como o serviço pode ser indisponibilizado?
- Elevation of Privilege: como alguém pode escalar permissões?

Para cada ameaça, dê:
1. Probabilidade (Alta/Média/Baixa)
2. Impacto (Critical/High/Medium/Low)
3. Mitigação recomendada
4. Categoria OWASP Top 10:2025 correspondente
```

---

## 10. 🚀 Code Review Rápido (Prompt Curto)

### Para colar direto no Copilot Chat ou review de PR:

```
Revise este código focando em: SQLi, IDOR, auth bypass,
hardcoded secrets, missing rate limit, error info leak.
Liste issues e fixes. Código:
```

```
Esse código é seguro para produção bancária?
Foque em OWASP Top 10:2025. Liste cada risco encontrado.
```

```
Reescreva este código aplicando: parametrized queries,
bcrypt, rate limiting, security headers, logging de segurança,
fail-closed error handling.
```

---

## ⚠️ Regras de Ouro ao Usar IA para Segurança

1. **Nunca cole secrets reais** em ferramentas externas (use placeholders)
2. **Valide TODA sugestão** — IA pode gerar código "quase seguro" mas com falhas sutis
3. **IA aumenta velocidade**, não substitui conhecimento
4. **Prompt injection é real** — não confie em dados que vieram de input externo como prompt
5. **Mantenha-se atualizado** — IA pode ter training data desatualizado sobre CVEs recentes
6. **Use IA interna** quando disponível (Copilot Enterprise, self-hosted) para código sensível

---

> *"A IA é o melhor segundo par de olhos que você pode ter — mas os olhos primários são os seus."*
