import smtplib
import logging
import ssl
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List
import re

from config.settings import Settings

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailService:
    """Serviço de envio de e-mails via SMTP com validação e proteção de templates."""

    VALID_TEMPLATES = {
        "boas_vindas",
        "manual_proprietario",
        "administradora_iptu",
    }

    def __init__(self):
        self.smtp_host = Settings.MAILTRAP_HOST
        self.smtp_port = Settings.MAILTRAP_PORT
        self.smtp_user = Settings.MAILTRAP_USER
        self.smtp_pass = Settings.MAILTRAP_PASS
        self.remetente = Settings.EMAIL_REMETENTE
        self.templates_dir = Settings.TEMPLATES_DIR

    def send_email(
        self,
        destinatario: str,
        cliente: Dict,
        template_name: str
    ) -> bool:
        """Envia e-mail personalizado usando template HTML, validando endereço e template."""

        if not EMAIL_REGEX.match(destinatario or ""):
            logger.error(f"E-mail inválido: {destinatario!r}")
            return False

        if template_name not in self.VALID_TEMPLATES:
            logger.error(f"Template inválido solicitado: {template_name!r}")
            return False

        try:
            html_body = self._load_and_personalize_template(template_name, cliente)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._get_subject(template_name, cliente.get('nome', ''))
            msg['From'] = self.remetente
            msg['To'] = destinatario

            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as smtp:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.login(self.smtp_user, self.smtp_pass)
                smtp.send_message(msg)

            logger.info(f"📧 E-mail '{template_name}' enviado para {destinatario}")
            return True

        except FileNotFoundError:
            logger.error(f"Template '{template_name}.html' não encontrado", exc_info=False)
            return False

except smtplib.SMTPException as e:
    logger.error(
        f"Erro SMTP ao enviar e-mail para {destinatario}: {type(e).__name__} - {e}",
        exc_info=False,
    )
    return False

        except Exception as e:
            logger.error(
                f"Erro inesperado ao enviar e-mail para {destinatario}: {type(e).__name__}",
                exc_info=False,
            )
            return False

    def send_multiple_emails(
        self,
        destinatario: str,
        cliente: Dict,
        template_names: List[str]
    ) -> Dict[str, bool]:
        """Envia múltiplos e-mails para o mesmo destinatário."""
        resultados = {}
        for template_name in template_names:
            resultados[template_name] = self.send_email(destinatario, cliente, template_name)
        return resultados

    def _load_and_personalize_template(
        self,
        template_name: str,
        cliente: Dict
    ) -> str:
        """Carrega template HTML e substitui placeholders, com proteção contra Path Traversal."""
        base_dir = self.templates_dir.resolve()
        template_path = (base_dir / f"{template_name}.html").resolve()

        if not str(template_path).startswith(str(base_dir)):
            raise ValueError(f"Tentativa de acesso indevido a template: {template_name}")

        html = template_path.read_text(encoding='utf-8')
        html = html.replace("NOME", cliente.get('nome', ''))
        return html

    @staticmethod
    def _get_subject(template_name: str, nome: str) -> str:
        """Gera assunto do e-mail baseado no template."""
        subjects = {
            # APROVAÇÃO
            "boas_vindas": f"Sua candidatura foi aprovada, {nome}! 🎉",
            # PRÓXIMOS PASSOS
            "manual_proprietario": f"Próximos passos do seu processo seletivo, {nome}",
            # REPROVAÇÃO
            "administradora_iptu": f"Atualização sobre sua candidatura, {nome}",
        }

        return subjects.get(
            template_name,
            f"Atualização do processo seletivo - {nome}"
        )


    def test_connection(self) -> bool:
        """Testa conectividade com servidor SMTP."""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as smtp:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.login(self.smtp_user, self.smtp_pass)

            logger.info("✅ Conexão com servidor SMTP estabelecida com sucesso!")
            return True

        except Exception as e:
            logger.error(f"Falha na conexão SMTP: {type(e).__name__}", exc_info=False)
            return False
