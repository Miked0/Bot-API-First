import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env')


class Settings:
    """Configurações centralizadas do sistema"""

    # HubSpot CRM API
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    HUBSPOT_BASE_URL = "https://api.hubapi.com/crm/v3/objects"

    # Mailtrap SMTP (Ambiente de Testes)
    MAILTRAP_HOST = os.getenv("MAILTRAP_HOST", "sandbox.smtp.mailtrap.io")
    MAILTRAP_PORT = int(os.getenv("MAILTRAP_PORT", "2525"))
    MAILTRAP_USER = os.getenv("MAILTRAP_USER")
    MAILTRAP_PASS = os.getenv("MAILTRAP_PASS")

    # Configurações de E-mail (sem default hardcoded)
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")

    # Caminhos do projeto
    DATA_SOURCE = BASE_DIR / "data" / "data_source.json"
    TEMPLATES_DIR = BASE_DIR / "templates"
    LOGS_DIR = BASE_DIR / "logs"
    LOG_FILE = LOGS_DIR / "processamento.log"

    # Rate limiting
    DELAY_BETWEEN_REQUESTS = 2  # segundos
    REQUEST_TIMEOUT = 10  # segundos

    @classmethod
    def validate(cls):
        """Valida se todas as variáveis essenciais estão configuradas e com formato básico correto."""
        required_vars = {
            "HUBSPOT_API_KEY": cls.HUBSPOT_API_KEY,
            "MAILTRAP_USER": cls.MAILTRAP_USER,
            "MAILTRAP_PASS": cls.MAILTRAP_PASS,
            "EMAIL_REMETENTE": cls.EMAIL_REMETENTE,
        }

        missing = [var for var, value in required_vars.items() if not (value and str(value).strip())]

        if missing:
            raise EnvironmentError(
                "\n❌ ERRO: Variáveis de ambiente faltando ou vazias: "
                + ", ".join(missing)
                + "\n\n📋 AÇÃO NECESSÁRIA:"
                + "\n1. Copie o arquivo .env.example para .env"
                + "\n2. Preencha as credenciais reais no arquivo .env"
                + "\n3. Execute o script novamente\n"
            )

        # Validação de formato da API Key HubSpot
        if not cls.HUBSPOT_API_KEY.startswith("pat-"):
            raise EnvironmentError(
                "HUBSPOT_API_KEY inválida. Deve começar com 'pat-'. "
                "Confirme o token copiado do Private App do HubSpot."
            )

        print("✅ Todas as configurações validadas com sucesso!")

    @classmethod
    def show_config(cls):
        """Exibe configurações atuais (sem expor credenciais)"""
        print("\n" + "=" * 60)
        print("⚙️  CONFIGURAÇÕES DO SISTEMA")
        print("=" * 60)
        print(f"HubSpot API: {'✅ Configurado' if cls.HUBSPOT_API_KEY else '❌ Não configurado'}")
        print(f"Mailtrap SMTP: {cls.MAILTRAP_HOST}:{cls.MAILTRAP_PORT}")
        print(f"Remetente: {cls.EMAIL_REMETENTE or 'NÃO CONFIGURADO'}")
        print(f"Fonte de dados: {cls.DATA_SOURCE}")
        print(f"Diretório de logs: {cls.LOGS_DIR}")
        print("=" * 60 + "\n")
