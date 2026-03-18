import requests
import logging
from typing import Dict, Optional

from config.settings import Settings

logger = logging.getLogger(__name__)


class HubSpotCRM:
    """Integração profissional com HubSpot CRM API v3"""

    def __init__(self):
        self.api_key = Settings.HUBSPOT_API_KEY
        self.base_url = Settings.HUBSPOT_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.timeout = Settings.REQUEST_TIMEOUT

    def create_ticket(self, cliente: Dict) -> Optional[str]:
        """Cria um ticket no HubSpot CRM."""
        endpoint = f"{self.base_url}/tickets"

        payload = {
            "properties": {
                "subject": f"Boas-vindas - {cliente.get('nome', '')}",
                "content": self._build_ticket_content(cliente),
                "hs_pipeline": "0",
                "hs_pipeline_stage": "1",
                "hs_ticket_priority": "MEDIUM",
            }
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            ticket_data = response.json()
            ticket_id = ticket_data['id']

            logger.info(
                f"✅ Ticket #{ticket_id} criado para {cliente.get('nome', '')} "
                f"({cliente.get('email', '')})"
            )

            return ticket_id

        except requests.exceptions.HTTPError as e:
            logger.error(
                "Erro HTTP ao criar ticket: %s - %s",
                getattr(e.response, 'status_code', 'N/A'),
                getattr(e.response, 'text', ''),
            )
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão ao criar ticket: {type(e).__name__}")
            return None

    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Consulta detalhes de um ticket específico."""
        endpoint = f"{self.base_url}/tickets/{ticket_id}"

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            ticket_data = response.json()
            logger.info(f"📋 Ticket #{ticket_id} consultado com sucesso")
            return ticket_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar ticket #{ticket_id}: {type(e).__name__}")
            return None

    def update_ticket(self, ticket_id: str, properties: Dict) -> bool:
        """Atualiza propriedades de um ticket."""
        endpoint = f"{self.base_url}/tickets/{ticket_id}"
        payload = {"properties": properties}

        try:
            response = requests.patch(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            logger.info(f"✏️  Ticket #{ticket_id} atualizado com sucesso")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao atualizar ticket #{ticket_id}: {type(e).__name__}")
            return False

    def _build_ticket_content(self, cliente: Dict) -> str:
        """Constrói conteúdo descritivo do ticket."""
        tipo = cliente.get('tipo_empreendimento', 'NÃO INFORMADO')

        content = f"""NOVO CLIENTE - PROCESSO DE BOAS-VINDAS

📋 DADOS DO CLIENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Nome: {cliente.get('nome', '')}
• E-mail: {cliente.get('email', '')}
• Empresa: {cliente.get('empresa', 'N/A')}
• Tipo de Empreendimento: {tipo}

🎯 AÇÕES PROGRAMADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Envio de e-mail de boas-vindas
"""

        if str(tipo).upper() == 'REMANESCENTE':
            content += """✓ Envio de manual do proprietário
✓ Envio de informações sobre administradora/IPTU
"""

        content += """

⏰ Ticket criado automaticamente pelo Bot CRM API
"""
        return content

    def test_connection(self) -> bool:
        """Testa conectividade com a API do HubSpot."""
        endpoint = f"{self.base_url}/tickets?limit=1"

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            logger.info("✅ Conexão com HubSpot API estabelecida com sucesso!")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Falha na conexão com HubSpot API: {type(e).__name__}")
            return False
