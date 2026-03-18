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
