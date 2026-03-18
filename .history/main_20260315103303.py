#!/usr/bin/env python3
"""Orquestrador principal do Bot CRM API-First."""

import json
import logging
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from config.settings import Settings
from modules.crm_module import HubSpotCRM
from modules.email_module import EmailService

# Logger de módulo seguro por default
logger = logging.getLogger("bot_crm_main")
logger.setLevel(logging.INFO)


def setup_logging() -> logging.Logger:
    """Configura sistema de logging (arquivo + console)."""
    Settings.LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger("bot_crm_main")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler_file = logging.FileHandler(Settings.LOG_FILE, encoding='utf-8')
        handler_stream = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        handler_file.setFormatter(formatter)
        handler_stream.setFormatter(formatter)

        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)

    return logger


CAMPOS_OBRIGATORIOS = ["nome", "email"]


def validate_cliente(cliente: Dict) -> Tuple[bool, List[str]]:
    """Valida schema mínimo do cliente (campos obrigatórios e tipos básicos)."""
    erros: List[str] = []

    for campo in CAMPOS_OBRIGATORIOS:
        valor = cliente.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            erros.append(f"Campo obrigatório inválido: {campo}")

    tipo_emp = cliente.get("tipo_empreendimento")
    if tipo_emp is not None and not isinstance(tipo_emp, str):
        erros.append("tipo_empreendimento deve ser string, se informado")

    return (len(erros) == 0, erros)


def load_clientes() -> List[Dict]:
    """Carrega base de clientes do arquivo JSON."""
    try:
        with open(Settings.DATA_SOURCE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        clientes = data.get('clientes', [])
        if not isinstance(clientes, list):
            logger.error("Formato inválido em data_source.json: 'clientes' não é lista")
            return []

        logger.info(f"📂 {len(clientes)} cliente(s) carregado(s) de {Settings.DATA_SOURCE.name}")
        return clientes

    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {Settings.DATA_SOURCE}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {type(e).__name__}")
        return []


def process_cliente(
    crm: HubSpotCRM,
    email_service: EmailService,
    cliente: Dict
) -> Dict:
    """Processa um cliente: cria ticket no CRM e envia e-mails."""
    resultado = {
        "nome": cliente.get('nome', ''),
        "email": cliente.get('email', ''),
        "empresa": cliente.get('empresa', 'N/A'),
        "tipo": cliente.get('tipo_empreendimento', 'N/A'),
        "status": "OK",
        "ticket_id": None,
        "emails_enviados": [],
        "erros": [],
    }

    logger.info("
" + "─" * 70)
    logger.info(f"👤 Processando: {resultado['nome']} | {resultado['email']}")
    logger.info(f"   Tipo: {resultado['tipo']}")
    logger.info("─" * 70)

    logger.info("🎫 [1/2] Criando ticket no HubSpot CRM...")
    ticket_id = crm.create_ticket(cliente)

    if not ticket_id:
        resultado['status'] = "ERRO"
        resultado['erros'].append("Falha ao criar ticket no CRM")
        logger.error(f"⛔ Não foi possível criar ticket para {resultado['nome']}")
        return resultado

    resultado['ticket_id'] = ticket_id

    logger.info("📧 [2/2] Enviando e-mails personalizados...")

    templates = ['boas_vindas']
    tipo = str(cliente.get('tipo_empreendimento', '')).upper()
    if tipo == 'REMANESCENTE':
        templates.extend(['manual_proprietario', 'administradora_iptu'])
        logger.info(f"   📋 Cliente REMANESCENTE: {len(templates)} e-mails programados")
    else:
        logger.info(f"   📋 Cliente {tipo or 'N/A'}: {len(templates)} e-mail programado")

    for template in templates:
        sucesso = email_service.send_email(
            destinatario=resultado['email'],
            cliente=cliente,
            template_name=template,
        )
        if sucesso:
            resultado['emails_enviados'].append(template)
        else:
            resultado['erros'].append(f"Falha ao enviar: {template}")

    if resultado['erros']:
        resultado['status'] = "PARCIAL" if resultado['emails_enviados'] else "ERRO"

    if resultado['status'] == 'OK':
        logger.info("✅ Cliente processado com sucesso!")
    elif resultado['status'] == 'PARCIAL':
        logger.warning(f"⚠️  Cliente processado parcialmente: {len(resultado['erros'])} erro(s)")
    else:
        logger.error("❌ Falha ao processar cliente")

    return resultado


def generate_report(resultados: List[Dict]) -> Dict:
    """Gera relatório consolidado dos processamentos."""
    total = len(resultados)
    total_ok = sum(1 for r in resultados if r['status'] == 'OK')
    total_parcial = sum(1 for r in resultados if r['status'] == 'PARCIAL')
    total_erro = sum(1 for r in resultados if r['status'] in ("ERRO", "ERRO_SCHEMA"))

    total_tickets = sum(1 for r in resultados if r.get('ticket_id'))
    total_emails = sum(len(r.get('emails_enviados', [])) for r in resultados)

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_clientes": total,
        "sucesso_completo": total_ok,
        "sucesso_parcial": total_parcial,
        "erros": total_erro,
        "tickets_criados": total_tickets,
        "emails_enviados": total_emails,
        "detalhes": resultados,
    }
    return report


def save_report(report: Dict):
    """Salva relatório em arquivo JSON."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = Settings.LOGS_DIR / f"relatorio_{timestamp}.json"

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"
💾 Relatório salvo em: {report_path}")


def print_banner():
    """Exibe banner inicial do sistema."""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║              🤖 BOT CRM - AUTOMAÇÃO VIA API 🤖                 ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"⏰ Execução iniciada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print("=" * 68 + "
")


def main():
    """Fluxo principal de execução."""
    global logger
    logger = setup_logging()

    print_banner()

    logger.info("🔍 Validando configurações...")
    try:
        Settings.validate()
        Settings.show_config()
    except EnvironmentError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("🚀 Inicializando serviços...")
    crm = HubSpotCRM()
    email_service = EmailService()

    logger.info("
🔌 Testando conectividade com APIs...")
    if not crm.test_connection():
        logger.error("❌ Falha na conexão com HubSpot. Verifique a API Key.")
        sys.exit(1)

    if not email_service.test_connection():
        logger.error("❌ Falha na conexão SMTP. Verifique as credenciais.")
        sys.exit(1)

    logger.info("✅ Todos os serviços conectados com sucesso!
")

    clientes = load_clientes()
    if not clientes:
        logger.error("❌ Nenhum cliente para processar. Verifique data_source.json")
        sys.exit(1)

    logger.info("
" + "═" * 68)
    logger.info(f"🎯 INICIANDO PROCESSAMENTO DE {len(clientes)} CLIENTE(S)")
    logger.info("═" * 68)

    resultados: List[Dict] = []

    for i, cliente in enumerate(clientes, 1):
        logger.info(f"
[{i}/{len(clientes)}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        valido, erros_schema = validate_cliente(cliente)
        if not valido:
            logger.error(f"Cliente ignorado por schema inválido: {erros_schema}")
            resultados.append({
                "nome": cliente.get('nome', ''),
                "email": cliente.get('email', ''),
                "empresa": cliente.get('empresa', 'N/A'),
                "tipo": cliente.get('tipo_empreendimento', 'N/A'),
                "status": "ERRO_SCHEMA",
                "ticket_id": None,
                "emails_enviados": [],
                "erros": erros_schema,
            })
            continue

        resultado = process_cliente(crm, email_service, cliente)
        resultados.append(resultado)

        if i < len(clientes):
            delay = Settings.DELAY_BETWEEN_REQUESTS
            logger.info(f"⏳ Aguardando {delay}s antes do próximo cliente...")
            time.sleep(delay)

    logger.info("
" + "═" * 68)
    logger.info("📊 RELATÓRIO FINAL DE EXECUÇÃO")
    logger.info("═" * 68)

    report = generate_report(resultados)

    logger.info("
📈 ESTATÍSTICAS:")
    logger.info(f"   • Total de clientes: {report['total_clientes']}")
    logger.info(f"   • ✅ Sucesso completo: {report['sucesso_completo']}")
    logger.info(f"   • ⚠️  Sucesso parcial: {report['sucesso_parcial']}")
    logger.info(f"   • ❌ Erros: {report['erros']}")

    logger.info("
📊 PRODUTIVIDADE:")
    logger.info(f"   • 🎫 Tickets criados: {report['tickets_criados']}")
    logger.info(f"   • 📧 E-mails enviados: {report['emails_enviados']}")

    save_report(report)

    logger.info("
" + "═" * 68)
    logger.info("✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
    logger.info(f"⏰ Finalizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    logger.info("═" * 68 + "
")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("

⚠️  Execução interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erro fatal: {type(e).__name__}", exc_info=True)
        sys.exit(1)
