# ⚡ GUIA DE INÍCIO RÁPIDO - 5 MINUTOS

## 🎯 Objetivo
Colocar o Bot CRM funcionando em 5 minutos usando ambientes de teste gratuitos.

---

## 📝 CHECKLIST DE CONFIGURAÇÃO

### ✅ Passo 1: Criar Conta HubSpot Developer (2 min)

1. Acesse: https://developers.hubspot.com/
2. Clique em **"Get started free"**
3. Preencha cadastro e confirme e-mail
4. No dashboard, clique em **"Create app"** → **"Create a private app"**
5. Configure permissões:
   - ✅ CRM → Tickets (Read + Write)
   - ✅ CRM → Contacts (Read)
6. Clique em **"Create app"**
7. **COPIE O TOKEN** (exemplo: `pat-na1-a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

---

### ✅ Passo 2: Criar Conta Mailtrap (1 min)

1. Acesse: https://mailtrap.io/
2. Clique em **"Sign Up"** → Use Google/GitHub para login rápido
3. No dashboard, vá em **"Email Testing"** → **"Inboxes"**
4. Clique no inbox **"Demo inbox"** ou crie um novo
5. Vá na aba **"SMTP Settings"**
6. **COPIE AS CREDENCIAIS:**
   ```
   Host: sandbox.smtp.mailtrap.io
   Port: 2525
   Username: (copie o seu)
   Password: (copie a sua)
   ```

---

### ✅ Passo 3: Configurar o Projeto (2 min)

1. **Abra o terminal** na pasta do projeto:
   ```bash
   cd bot-crm-api
   ```

2. **Crie ambiente virtual Python:**
   ```bash
   python -m venv venv

   # Ativar:
   # Windows:
   venv\Scripts\activate

   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure variáveis de ambiente:**
   ```bash
   # Copiar template
   cp .env.example .env
   ```

5. **Edite o arquivo `.env`** com suas credenciais:
   ```env
   HUBSPOT_API_KEY=cole_seu_token_hubspot_aqui
   MAILTRAP_HOST=sandbox.smtp.mailtrap.io
   MAILTRAP_PORT=2525
   MAILTRAP_USER=cole_seu_username_mailtrap
   MAILTRAP_PASS=cole_sua_senha_mailtrap
   EMAIL_REMETENTE=relacionamento@eztec.com.br
   ```

---

### ✅ Passo 4: Testar Conexões

```bash
python quick_test.py
```

**Resultado esperado:**
```
✅ Todas as variáveis de ambiente configuradas
✅ Conexão com HubSpot OK
✅ Conexão SMTP OK
✅ Todos os arquivos presentes
🚀 Sistema pronto para execução!
```

---

### ✅ Passo 5: Executar o Bot!

```bash
python main.py
```

---

## 🎉 Sucesso!

Você verá algo como:

```
╔════════════════════════════════════════╗
║      🤖 BOT CRM - AUTOMAÇÃO VIA API    ║
╚════════════════════════════════════════╝

✅ Conexão com HubSpot API estabelecida!
✅ Conexão com servidor SMTP estabelecida!

📂 3 cliente(s) carregado(s)

🎯 INICIANDO PROCESSAMENTO...

[1/3] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Processando: Ana Silva
✅ Ticket #12345678 criado
📧 E-mail 'boas_vindas' enviado
📧 E-mail 'manual_proprietario' enviado
📧 E-mail 'administradora_iptu' enviado
✅ Cliente processado com sucesso!

...

📊 RELATÓRIO FINAL
   • Total de clientes: 3
   • ✅ Sucesso completo: 3
   • 🎫 Tickets criados: 3
   • 📧 E-mails enviados: 7

✅ EXECUÇÃO CONCLUÍDA!
```

---

## 🔍 Onde Ver os Resultados?

### **Tickets no HubSpot:**
1. Acesse: https://app.hubspot.com/
2. Menu lateral → **Service** → **Tickets**
3. Você verá os tickets criados: "Boas-vindas - [Nome]"

### **E-mails no Mailtrap:**
1. Acesse: https://mailtrap.io/inboxes
2. Clique no seu inbox
3. Você verá todos os e-mails enviados (sem envio real!)

### **Relatórios Locais:**
- **Log detalhado:** `logs/processamento.log`
- **Relatório JSON:** `logs/relatorio_YYYYMMDD_HHMMSS.json`

---

## ❌ Problemas Comuns?

### "Variáveis de ambiente faltando"
→ Verifique se arquivo `.env` existe e está preenchido

### "Falha na conexão HubSpot"
→ Confirme que copiou o token completo (começa com `pat-`)

### "Falha na conexão SMTP"
→ Confirme que copiou username/password do Mailtrap corretamente

### "Template não encontrado"
→ Execute novamente o setup, arquivos podem não ter sido criados

---

## 🚀 Próximos Passos

Após validar que tudo funciona:

1. **Adicionar clientes reais** em `data/data_source.json`
2. **Personalizar templates** em `templates/*.html`
3. **Migrar para produção:**
   - HubSpot: Use conta real (não developer)
   - E-mail: Substitua Mailtrap por SMTP corporativo

---

## 🆘 Precisa de Ajuda?

Consulte o **README.md** completo para:
- Documentação detalhada
- Troubleshooting avançado
- Personalização de módulos

**Boa automação! 🎉**
