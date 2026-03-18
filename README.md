# 🤖 Bot CRM API-First — Orquestrador de Processos Seletivos

Um orquestrador construído em Python projetado para automatizar o fluxo de comunicação em processos seletivos. A aplicação aplica conceitos *Lean* para eliminar tarefas manuais, integrando o **HubSpot CRM (via API v3)** e disparando e-mails dinâmicos (via SMTP) com base no status de progressão de cada candidato no pipeline.

---

## 📋 Índice
- [Visão Geral](#-visão-geral)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Base de Dados e Templates](#-base-de-dados-e-templates)
- [Execução e Fluxo](#-execução-e-fluxo)
- [Monitoramento: Logs e Relatórios](#-monitoramento-logs-e-relatórios)
- [Tratamento de Erros e Trade-offs](#-tratamento-de-erros-e-trade-offs)

---

## 🎯 Visão Geral

O bot atua como um *middleware* entre uma base de dados estruturada (JSON) e as plataformas de operação. Ele valida os *schemas* dos candidatos, orquestra a criação de tickets no HubSpot contendo o contexto completo da candidatura e gerencia o disparo de e-mails HTML personalizados.

| Status do Candidato | Ticket no CRM | Ação de E-mail (SMTP) |
| :--- | :---: | :--- |
| `APROVADO` | ✅ Criado | Dispara `aprovacao_candidatura.html` + `proximos_passos.html` |
| `REPROVADO` | ✅ Criado | Dispara `reprovacao_candidatura.html` |
| `EM_ANALISE` | ✅ Criado | *Nenhuma (Aguardando decisão manual no pipeline)* |

---

## 🗂 Arquitetura do Projeto

A estrutura foi desenhada visando a separação de responsabilidades (SoC) e facilidade de manutenção:

```text
bot_crm/
├── config/
│   └── settings.py          # Gerenciamento de env vars e configs globais
├── data/
│   └── data_source.json     # Base de input de candidatos (Schema validado)
├── logs/
│   ├── processo_seletivo.log    # Log transacional de execução
│   └── relatorio_*.json         # Output de relatórios analíticos gerados
├── modules/
│   ├── crm_module.py        # Wrapper de integração HubSpot CRM API v3
│   └── email_module.py      # Serviço SMTP, renderização de templates e rate limit
├── templates/
│   ├── aprovacao_candidatura.html
│   ├── proximos_passos.html
│   └── reprovacao_candidatura.html
├── main.py                  # Orquestrador principal / Entrypoint
├── quick_test.py            # Script de Health Check (API/SMTP)
├── .env.example             # Template de credenciais
└── requirements.txt
```

---

## 🛠 Tecnologias Utilizadas

| Componente | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Core** | Python 3.10+ | Lógica de orquestração e processamento de dados. |
| **Integração** | Requests / HubSpot API v3 | Manipulação de recursos RESTful no CRM. |
| **Comunicação** | `smtplib` / `ssl` | Conexão STARTTLS e disparo de e-mails. |
| **Configuração** | `python-dotenv` | Injeção de dependências via variáveis de ambiente. |
| **Observabilidade** | `logging` nativo | Rastreabilidade de fluxos e tratamento de exceções. |

---

## ✅ Pré-requisitos

- Python 3.10+ instalado.
- Conta e *Private App Token* no [HubSpot CRM](https://hubspot.com).
- Servidor SMTP para testes (recomendado: [Mailtrap](https://mailtrap.io)) ou produção (ex: AWS SES, SendGrid).

---

## 🚀 Instalação e Configuração

### 1. Setup do Ambiente
```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/bot-crm-api-first.git](https://github.com/seu-usuario/bot-crm-api-first.git)
cd bot-crm-api-first

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração de Credenciais
Crie o arquivo `.env` baseado no exemplo fornecido:
```bash
cp .env.example .env
```
Edite o `.env` com suas credenciais:
```ini
# HubSpot
HUBSPOT_API_KEY=seu_token_aqui

# SMTP (Ex: Mailtrap)
MAILTRAP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_PORT=2525
MAILTRAP_USER=usuario
MAILTRAP_PASS=senha

# Remetente
EMAIL_REMETENTE=ta@suaempresa.com
```
> ⚠️ **Segurança:** O arquivo `.env` já está no `.gitignore`. Nunca versione credenciais ou dados sensíveis de candidatos.

---

## 📦 Base de Dados e Templates

### Formato de Entrada (`data/data_source.json`)
O sistema espera uma lista de objetos JSON. Os campos `nome` e `email` são estritamente obrigatórios para aprovação no *schema*.

```json
{
  "clientes": [
    {
      "nome": "Ana Martins",
      "email": "ana.martins@example.com",
      "vaga": "Engenheira de Software Pleno",
      "status_candidatura": "APROVADO",
      "etapa": "ENTREVISTA_FINAL"
    }
  ]
}
```

### Personalização de E-mails
Os templates HTML localizados na pasta `/templates` suportam injeção dinâmica. A tag `NOME` (em uppercase) atua como um *placeholder* que será substituído no momento do disparo em tempo de execução.

---

## ▶️ Execução e Fluxo

### 1. Health Check (Recomendado)
Antes de rodar a base principal, valide as conexões com as APIs de terceiros:
```bash
python quick_test.py
```

### 2. Execução do Pipeline Principal
```bash
python main.py
```

### Fluxo Lógico do Orquestrador:
1. Validação de *Environment* e *Health Check* de conectividade.
2. Ingestão e validação do *schema* de candidatos via JSON.
3. *Loop* de processamento:
   - Requisição POST para o HubSpot (Criação de Ticket).
   - Análise de condicional de `status_candidatura`.
   - Disparo assíncrono simulado via SMTP injetando os templates adequados.
4. Aplicação de lógicas de *Rate Limiting* (Delay entre requisições).
5. Consolidação de métricas e exportação de relatório final.

---

## 📊 Monitoramento: Logs e Relatórios

O sistema possui observabilidade nativa, gravando no console e em arquivos simultaneamente.

**Exemplo de Log de Execução (`logs/processo_seletivo.log`):**
```text
2026-03-17 21:00:00 | INFO | 👤 Processando: Ana Martins | ana.martins@example.com
2026-03-17 21:00:01 | INFO | 🎫 [1/2] Criando ticket no HubSpot CRM...
2026-03-17 21:00:03 | INFO | ⏩ Enviando e-mail 1/2 (aprovacao_candidatura)...
2026-03-17 21:00:18 | INFO | ✅ Candidato processado com sucesso!
```

**Relatório Analítico (`logs/relatorio_*.json`):**
Gera um *snapshot* de cada execução para auditoria.
```json
{
  "total_clientes": 10,
  "sucesso_completo": 7,
  "sucesso_parcial": 2,
  "erros": 1,
  "tickets_criados": 10,
  "emails_enviados": 14
}
```

---

## 🛡 Tratamento de Erros e Trade-offs

A arquitetura foi pensada para resiliência de rede e controle de *throttling*:

| Incidente | Causa | Comportamento do Sistema |
| :--- | :--- | :--- |
| **ERRO_SCHEMA** | `nome` ou `email` ausente/inválido. | Candidato é ignorado (Fail-fast). Não consome cota de API. |
| **FALHA API** | HubSpot indisponível ou Timeout. | Candidato classificado como `ERRO`. E-mails não são disparados. |
| **SMTP 550** | *Rate Limit* excedido no provedor. | O sistema implementa um *delay* configurável (`DELAY_ENTRE_EMAILS`) para mitigar bloqueios. |
| **FALHA PARCIAL** | Ticket criado, mas SMTP falhou. | Ticket mantido no CRM. Relatório marca candidato como `PARCIAL`. |

> **📌 Limitações Conhecidas (Tech Debt):** > - **Idempotência:** Atualmente, a aplicação não gerencia estado de execuções anteriores. Rodar o mesmo JSON duas vezes gerará tickets duplicados. Solução futura: Implementar verificação de *hash* ou checagem de e-mail existente na API antes do POST.
> - **SMTP em Produção:** Os *delays* atuais são otimizados para provedores gratuitos (como Mailtrap). Em produção real, o uso de provedores focados em transacionais (AWS SES, SendGrid) permite reduzir o *delay* a zero.

---

### 👤 Autor
**Mike** Desenvolvedor Full-Stack | Arquiteto de Soluções & Automação Lean  
```

