🛠 Tecnologias UtilizadasComponenteTecnologiaPropósitoCorePython 3.10+Lógica de orquestração e processamento de dados.IntegraçãoRequests / HubSpot API v3Manipulação de recursos RESTful no CRM.Comunicaçãosmtplib / sslConexão STARTTLS e disparo de e-mails.Configuraçãopython-dotenvInjeção de dependências via variáveis de ambiente.Observabilidadelogging nativoRastreabilidade de fluxos e tratamento de exceções.✅ Pré-requisitosPython 3.10+ instalado.Conta e Private App Token no HubSpot CRM.Servidor SMTP para testes (recomendado: Mailtrap) ou produção (ex: AWS SES, SendGrid).🚀 Instalação e Configuração1. Setup do AmbienteBash# Clone o repositório
git clone [https://github.com/seu-usuario/bot-crm-api-first.git](https://github.com/seu-usuario/bot-crm-api-first.git)
cd bot-crm-api-first

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
2. Configuração de CredenciaisCrie o arquivo .env baseado no exemplo fornecido:Bashcp .env.example .env
Edite o .env com suas credenciais:Ini, TOML# HubSpot
HUBSPOT_API_KEY=seu_token_aqui

# SMTP (Ex: Mailtrap)
MAILTRAP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_PORT=2525
MAILTRAP_USER=usuario
MAILTRAP_PASS=senha

# Remetente
EMAIL_REMETENTE=ta@suaempresa.com
⚠️ Segurança: O arquivo .env já está no .gitignore. Nunca versione credenciais ou dados sensíveis de candidatos.📦 Base de Dados e TemplatesFormato de Entrada (data/data_source.json)O sistema espera uma lista de objetos JSON. Os campos nome e email são estritamente obrigatórios para aprovação no schema.JSON{
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
Personalização de E-mailsOs templates HTML localizados na pasta /templates suportam injeção dinâmica. A tag NOME (em uppercase) atua como um placeholder que será substituído no momento do disparo em tempo de execução.▶️ Execução e Fluxo1. Health Check (Recomendado)Antes de rodar a base principal, valide as conexões com as APIs de terceiros:Bashpython quick_test.py
2. Execução do Pipeline PrincipalBashpython main.py
Fluxo Lógico do Orquestrador:Validação de Environment e Health Check de conectividade.Ingestão e validação do schema de candidatos via JSON.Loop de processamento:Requisição POST para o HubSpot (Criação de Ticket).Análise de condicional de status_candidatura.Disparo assíncrono simulado via SMTP injetando os templates adequados.Aplicação de lógicas de Rate Limiting (Delay entre requisições).Consolidação de métricas e exportação de relatório final.📊 Monitoramento: Logs e RelatóriosO sistema possui observabilidade nativa, gravando no console e em arquivos simultaneamente.Exemplo de Log de Execução (logs/processo_seletivo.log):Plaintext2026-03-17 21:00:00 | INFO | 👤 Processando: Ana Martins | ana.martins@example.com
2026-03-17 21:00:01 | INFO | 🎫 [1/2] Criando ticket no HubSpot CRM...
2026-03-17 21:00:03 | INFO | ⏩ Enviando e-mail 1/2 (aprovacao_candidatura)...
2026-03-17 21:00:18 | INFO | ✅ Candidato processado com sucesso!
Relatório Analítico (logs/relatorio_*.json):Gera um snapshot de cada execução para auditoria.JSON{
  "total_clientes": 10,
  "sucesso_completo": 7,
  "sucesso_parcial": 2,
  "erros": 1,
  "tickets_criados": 10,
  "emails_enviados": 14
}
🛡 Tratamento de Erros e Trade-offsA arquitetura foi pensada para resiliência de rede e controle de throttling:IncidenteCausaComportamento do SistemaERRO_SCHEMAnome ou email ausente/inválido.Candidato é ignorado (Fail-fast). Não consome cota de API.FALHA APIHubSpot indisponível ou Timeout.Candidato classificado como ERRO. E-mails não são disparados.SMTP 550Rate Limit excedido no provedor.O sistema implementa um delay configurável (DELAY_ENTRE_EMAILS) para mitigar bloqueios.FALHA PARCIALTicket criado, mas SMTP falhou.Ticket mantido no CRM. Relatório marca candidato como PARCIAL.📌 Limitações Conhecidas (Tech Debt): > - Idempotência: Atualmente, a aplicação não gerencia estado de execuções anteriores. Rodar o mesmo JSON duas vezes gerará tickets duplicados. Solução futura: Implementar verificação de hash ou checagem de e-mail existente na API antes do POST.SMTP em Produção: Os delays atuais são otimizados para provedores gratuitos (como Mailtrap). Em produção real, o uso de provedores focados em transacionais (AWS SES, SendGrid) permite reduzir o delay a zero.👤 AutorMike Desenvolvedor Full-Stack | Arquiteto de Soluções & Automação Lean
