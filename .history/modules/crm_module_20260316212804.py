import requests
import logging
from typing import Dict, Optional

from config.settings import Settings

logger = logging.getLogger(__name__)


class HubSpotCRM:
    """Integração profissional com HubSpot CRM API v3 para processo seletivo."""

    def __init__(self):
        self.api_key = Settings.HUBSPOT_API_KEY
        self.base_url = Settings.HUBSPOT_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.timeout = Settings.REQUEST_TIMEOUT

    def create_ticket(self, cliente: Dict) -> Optional[str]:
        """Cria um ticket no HubSpot CRM com contexto de recrutamento."""
        endpoint = f"{self.base_url}/tickets"

        vaga = cliente.get('vaga', 'Vaga não informada')
        status_cand = str(cliente.get('status_candidatura', 'EM_ANALISE')).upper()

        if status_cand == 'APROVADO':
            subject = f"Candidato APROVADO - {vaga} - {cliente.get('nome', '')}"
        elif status_cand == 'REPROVADO':
            subject = f"Candidato REPROVADO - {vaga} - {cliente.get('nome', '')}"
        else:
            subject = f"Candidatura EM ANÁLISE - {vaga} - {cliente.get('nome', '')}"

        payload = {
            "properties": {
                "subject": subject,
                "content": self._build_ticket_content(cliente),
                "hs_pipeline": "0",          # Pipeline padrão (ajuste se tiver outro para recrutamento)
                "hs_pipeline_stage": "1",    # Estágio inicial
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
        """Constrói conteúdo descritivo do ticket para processo seletivo."""
        vaga = cliente.get('vaga', 'Vaga não informada')
        status_cand = str(cliente.get('status_candidatura', 'EM_ANALISE')).upper()
        etapa = cliente.get('etapa', 'Etapa não informada')

        status_legivel = {
            'APROVADO': 'Aprovado(a)',
            'REPROVADO': 'Reprovado(a)',
            'EM_ANALISE': 'Em análise'
        }.get(status_cand, status_cand.title())

        content = f"""PROCESSO SELETIVO - TALENTHUB

📋 DADOS DO CANDIDATO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Nome: {cliente.get('nome', '')}
• E-mail: {cliente.get('email', '')}
• Origem: {cliente.get('empresa', 'Candidato Independente')}

📌 INFORMAÇÕES DA VAGA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Vaga: {vaga}
• Status da candidatura: {status_legivel}
• Etapa atual: {etapa}

🎯 CONTEXTO DO ATENDIMENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if status_cand == 'APROVADO':
            content += (
                "Candidato aprovado na etapa atual do processo seletivo. "
                "Foram enviados e-mails automáticos de aprovação e próximos passos.\n"
            )
        elif status_cand == 'REPROVADO':
            content += (
                "Candidato não seguirá adiante neste processo seletivo. "
                "Foi enviado e-mail automático de comunicação da decisão.\n"
            )
        else:
            content += (
                "Candidatura em análise. Nenhum e-mail automático foi enviado neste momento. "
                "Aguardando decisão do time de Talent Acquisition.\n"
            )

        content += """

🔁 AÇÕES SUGERIDAS À EQUIPE DE TALENT ACQUISITION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Registrar feedback interno sobre o candidato.
• Atualizar manualmente o status da vaga/candidatura no CRM, se necessário.
• Manter histórico de interação para futuras oportunidades.

⏰ Ticket criado automaticamente pelo Bot CRM API - Fluxo de Processo Seletivo
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
