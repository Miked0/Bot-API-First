text
# 🤖 Bot CRM API-First — Automação de Processo Seletivo

Orquestrador Python que automatiza o fluxo de comunicação de um processo
seletivo, integrando HubSpot CRM (via API v3) e disparo de e-mails
personalizados (via SMTP), com base no status de cada candidato.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura do Projeto](#arquitetura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Base de Dados](#base-de-dados)
- [Templates de E-mail](#templates-de-e-mail)
- [Como Executar](#como-executar)
- [Fluxo de Processamento](#fluxo-de-processamento)
- [Logs e Relatórios](#logs-e-relatórios)
- [Tratamento de Erros](#tratamento-de-erros)
- [Limitações Conhecidas](#limitações-conhecidas)

---

## 🎯 Visão Geral

O bot lê uma base de candidatos em JSON, valida os dados, cria um ticket
no HubSpot CRM com o contexto completo da candidatura e dispara e-mails
HTML personalizados de acordo com o status de cada pessoa:

| Status | Tickets criados | E-mails disparados |
|---|---|---|
| `APROVADO` | ✅ Sim | `aprovacao_candidatura` + `proximos_passos` |
| `REPROVADO` | ✅ Sim | `reprovacao_candidatura` |
| `EM_ANALISE` | ✅ Sim | Nenhum (aguarda decisão manual) |

---

## 🗂 Arquitetura do Projeto

bot_teste/
│
├── config/
│ └── settings.py # Variáveis de ambiente e configurações globais
│
├── data/
│ └── data_source.json # Base de candidatos
│
├── logs/
│ ├── processo_seletivo.log # Log completo de execução
│ └── relatorio_*.json # Relatórios por execução (gerados automaticamente)
│
├── modules/
│ ├── crm_module.py # Integração HubSpot CRM API v3
│ └── email_module.py # Serviço SMTP com validação e templates
│
├── templates/
│ ├── aprovacao_candidatura.html # E-mail de aprovação
│ ├── proximos_passos.html # E-mail com próximos passos
│ └── reprovacao_candidatura.html # E-mail de reprovação
│
├── main.py # Orquestrador principal
├── quick_test.py # Validação rápida do ambiente
├── .env # Credenciais (não versionar)
├── .env.example # Exemplo de variáveis necessárias
├── .gitignore
└── requirements.txt

text

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| Requests | 2.31+ | Integração HubSpot REST API v3 |
| smtplib | nativo | Envio de e-mails via SMTP |
| ssl | nativo | Conexão segura STARTTLS |
| python-dotenv | 1.0+ | Leitura de variáveis de ambiente |
| logging | nativo | Logs estruturados (arquivo + console) |
| HubSpot CRM API v3 | — | Criação e gerenciamento de tickets |
| Mailtrap | — | Servidor SMTP (ambiente de testes) |

---

## ✅ Pré-requisitos

- Python 3.10 ou superior
- Conta ativa no [HubSpot](https://hubspot.com) com API Key gerada
- Conta ativa no [Mailtrap](https://mailtrap.io) para testes SMTP
- Git instalado (opcional, para clonar o repositório)

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/bot-crm-api-first.git
cd bot-crm-api-first
2. Crie e ative o ambiente virtual
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
bash
pip install -r requirements.txt
⚙️ Configuração
1. Crie o arquivo .env
Copie o arquivo de exemplo:

bash
cp .env.example .env
2. Preencha as variáveis no .env
text
# HubSpot
HUBSPOT_API_KEY=seu_token_aqui

# Mailtrap SMTP
MAILTRAP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_PORT=2525
MAILTRAP_USER=seu_usuario_mailtrap
MAILTRAP_PASS=sua_senha_mailtrap

# Remetente
EMAIL_REMETENTE=seuemail@dominio.com
⚠️ Nunca versione o arquivo .env.
Ele já está listado no .gitignore.

📦 Base de Dados
O arquivo data/data_source.json contém a lista de candidatos a processar.

Estrutura esperada
json
{
  "clientes": [
    {
      "nome": "Ana Martins",
      "email": "ana.martins@example.com",
      "empresa": "Candidato Independente",
      "vaga": "Analista de Suporte",
      "status_candidatura": "APROVADO",
      "etapa": "ENTREVISTA_FINAL"
    }
  ]
}
Campos
Campo	Tipo	Obrigatório	Descrição
nome	string	✅ Sim	Nome completo do candidato
email	string	✅ Sim	E-mail válido para contato
empresa	string	Não	Empresa de origem (ou "Candidato Independente")
vaga	string	Não	Nome da vaga pretendida
status_candidatura	string	Não	APROVADO, REPROVADO ou EM_ANALISE
etapa	string	Não	Etapa atual do funil (ex: ENTREVISTA_FINAL)
📧 Templates de E-mail
Os templates ficam em templates/ e são arquivos HTML com o placeholder
NOME, substituído dinamicamente pelo nome do candidato em cada envio.

Arquivo	Gatilho	Conteúdo
aprovacao_candidatura.html	Status APROVADO	Parabéns pela aprovação e próximas etapas
proximos_passos.html	Status APROVADO	Detalhamento do que o candidato deve fazer
reprovacao_candidatura.html	Status REPROVADO	Feedback respeitoso e manutenção no banco de talentos
Como personalizar um template
Abra o arquivo HTML desejado em templates/.

Edite o conteúdo livremente.

Mantenha o placeholder NOME onde quiser que o nome do candidato apareça.

Não renomeie os arquivos sem atualizar VALID_TEMPLATES em email_module.py.

▶️ Como Executar
Validação rápida do ambiente (recomendado antes de rodar)
bash
python quick_test.py
Verifica:

Variáveis de ambiente configuradas.

Arquivos de template presentes.

Conexão com HubSpot API.

Conexão com servidor SMTP.

Execução principal
bash
python main.py
🔄 Fluxo de Processamento
text
Início
  │
  ├── Valida configurações (.env)
  ├── Inicializa HubSpotCRM e EmailService
  ├── Testa conectividade (HubSpot + SMTP)
  ├── Carrega candidatos do data_source.json
  │
  └── Para cada candidato:
        │
        ├── Valida schema (nome + email obrigatórios)
        ├── Cria ticket no HubSpot CRM
        │     └── Subject: "Candidato APROVADO/REPROVADO/EM ANÁLISE - Vaga - Nome"
        │
        ├── Define templates por status:
        │     ├── APROVADO   → aprovacao_candidatura + proximos_passos
        │     ├── REPROVADO  → reprovacao_candidatura
        │     └── EM_ANALISE → nenhum e-mail
        │
        ├── Envia e-mails (com delay de 15s entre cada um)
        ├── Aguarda 8s antes do próximo candidato
        │
        └── Registra resultado: OK / PARCIAL / ERRO
  │
  └── Gera relatório JSON + encerra execução
📊 Logs e Relatórios
Log de execução
Localização: logs/processo_seletivo.log

Formato:

text
2026-03-17 21:00:00 | INFO     | 👤 Processando: Ana Martins | ana.martins@example.com
2026-03-17 21:00:01 | INFO     | 🎫 [1/2] Criando ticket no HubSpot CRM...
2026-03-17 21:00:03 | INFO     |    ⏩ Enviando e-mail 1/2 (aprovacao_candidatura)...
2026-03-17 21:00:18 | INFO     |    ⏩ Enviando e-mail 2/2 (proximos_passos)...
2026-03-17 21:00:20 | INFO     | ✅ Candidato processado com sucesso!
Relatório JSON
Gerado automaticamente a cada execução em:

text
logs/relatorio_YYYYMMDD_HHMMSS.json
Estrutura:

json
{
  "timestamp": "2026-03-17T21:00:00",
  "total_clientes": 10,
  "sucesso_completo": 7,
  "sucesso_parcial": 2,
  "erros": 1,
  "tickets_criados": 10,
  "emails_enviados": 14,
  "detalhes": [...]
}
🛡 Tratamento de Erros
Erro	Causa	Comportamento
ERRO_SCHEMA	nome ou email ausente/inválido	Candidato ignorado, sem ticket ou e-mail
ERRO (ticket)	Falha na API HubSpot	Candidato marcado como ERRO, sem e-mails
PARCIAL	Ticket OK, algum e-mail falhou	Registra quais templates foram enviados e quais falharam
SMTPDataError 550	Rate limit do Mailtrap	Aumentar DELAY_ENTRE_EMAILS em main.py
SMTPServerDisconnected	Bloqueio temporário do servidor	Aguardar 2–3 minutos e reexecutar
⚠️ Limitações Conhecidas
Mailtrap (plano gratuito): Limite de envio por segundo. O bot usa delays
configuráveis (DELAY_ENTRE_EMAILS = 15s, DELAY_BETWEEN_REQUESTS = 8s)
para respeitar esse limite. Em produção, use um provedor SMTP sem rate limit
(ex: SendGrid, Amazon SES).

Reprocessamento: O bot não verifica se um candidato já foi processado
anteriormente. Rodar duas vezes com o mesmo data_source.json criará
tickets duplicados no HubSpot.

EM_ANALISE: Candidatos com esse status têm ticket criado mas não recebem
e-mail automático. A comunicação para esse grupo deve ser feita manualmente
ou via um novo template futuro.

👤 Autor
Desenvolvido por Mike
Assistente de Relacionamento com o Cliente | Automação & Processos