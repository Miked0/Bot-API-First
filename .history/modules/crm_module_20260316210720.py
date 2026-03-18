    logger.info("📧 [2/2] Enviando e-mails personalizados...")

    # NOVA LÓGICA: escolher templates com base no status da candidatura
    status_cand = str(cliente.get('status_candidatura', '')).upper()

    templates: List[str] = []

    if status_cand == 'APROVADO':
        # 1) E-mail de aprovação
        # 2) E-mail com próximos passos
        templates = ['boas_vindas', 'manual_proprietario']
        logger.info(f"   📋 Candidato APROVADO: {len(templates)} e-mails programados")
    elif status_cand == 'REPROVADO':
        # E-mail de reprovação
        templates = ['administradora_iptu']
        logger.info(f"   📋 Candidato REPROVADO: {len(templates)} e-mail programado")
    else:
        # EM_ANALISE ou qualquer outro status: por enquanto, sem e-mails automáticos
        templates = []
        logger.info(f"   📋 Candidato com status {status_cand or 'N/A'}: nenhum e-mail automático será enviado")

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
