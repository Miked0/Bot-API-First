#!/usr/bin/env python3
"""
Script de Teste Rápido - Validação do Ambiente
Valida configurações e conectividade sem processar clientes
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings
from modules.crm_module import HubSpotCRM
from modules.email_module import EmailService


def test_environment():
    """Testa configurações e conectividade"""

    print("\n" + "="*60)
    print("🧪 TESTE RÁPIDO DE AMBIENTE")
    print("="*60 + "\n")

    # Teste 1: Validar configurações
    print("📋 [1/4] Validando configurações...")
    try:
        Settings.validate()
        print("   ✅ Todas as variáveis de ambiente configuradas\n")
    except EnvironmentError as e:
        print(f"   ❌ ERRO: {e}")
        return False

    # Teste 2: Conectividade HubSpot
    print("🔌 [2/4] Testando conexão com HubSpot API...")
    crm = HubSpotCRM()
    if crm.test_connection():
        print("   ✅ Conexão com HubSpot OK\n")
    else:
        print("   ❌ Falha na conexão com HubSpot")
        return False

    # Teste 3: Conectividade SMTP
    print("📧 [3/4] Testando conexão SMTP (Mailtrap)...")
    email_service = EmailService()
    if email_service.test_connection():
        print("   ✅ Conexão SMTP OK\n")
    else:
        print("   ❌ Falha na conexão SMTP")
        return False

    # Teste 4: Verificar arquivos essenciais
    print("📁 [4/4] Verificando arquivos essenciais...")

    arquivos_essenciais = [
        Settings.DATA_SOURCE,
        Settings.TEMPLATES_DIR / "aprovacao_candidatura.html",
        Settings.TEMPLATES_DIR / "proximos_passos.html",
        Settings.TEMPLATES_DIR / "administradora_iptu.html"
    ]

    todos_ok = True
    for arquivo in arquivos_essenciais:
        if arquivo.exists():
            print(f"   ✅ {arquivo.name}")
        else:
            print(f"   ❌ FALTANDO: {arquivo.name}")
            todos_ok = False

    if not todos_ok:
        return False

    print("\n" + "="*60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*60)
    print("\n🚀 Sistema pronto para execução!")
    print("   Execute: python main.py\n")

    return True


if __name__ == "__main__":
    try:
        sucesso = test_environment()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        sys.exit(1)
