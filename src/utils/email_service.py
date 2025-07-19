import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configurações de email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'agendamontereletrica@gmail.com'
EMAIL_PASSWORD = 'cent dvbi wgxc acjd'  # App password fornecida pelo usuário

def enviar_email(destinatario, assunto, corpo_html, corpo_texto=None):
    """
    Envia um email para o destinatário especificado
    """
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        # Adicionar corpo do email
        if corpo_texto:
            part1 = MIMEText(corpo_texto, 'plain', 'utf-8')
            msg.attach(part1)
        
        part2 = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(part2)
        
        # Conectar ao servidor SMTP
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Enviar email
        text = msg.as_string()
        server.sendmail(EMAIL_USER, destinatario, text)
        server.quit()
        
        logging.info(f"Email enviado com sucesso para {destinatario}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao enviar email para {destinatario}: {str(e)}")
        return False

def enviar_notificacao_agendamento(reuniao, participantes):
    """
    Envia notificação de agendamento de reunião para todos os participantes
    """
    data_inicio = reuniao.data_inicio.strftime('%d/%m/%Y às %H:%M')
    data_fim = reuniao.data_fim.strftime('%d/%m/%Y às %H:%M')
    
    assunto = f"Nova Reunião Agendada: {reuniao.titulo}"
    
    # Template HTML do email
    corpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
            .info-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Nova Reunião Agendada</h1>
            </div>
            <div class="content">
                <p>Olá!</p>
                
                <p>Uma nova reunião foi agendada e você foi convidado(a) para participar.</p>
                
                <div class="info-box">
                    <h3>📋 Detalhes da Reunião</h3>
                    <p><strong>Título:</strong> {reuniao.titulo}</p>
                    <p><strong>Descrição:</strong> {reuniao.descricao or 'Sem descrição'}</p>
                    <p><strong>Data e Hora de Início:</strong> {data_inicio}</p>
                    <p><strong>Data e Hora de Término:</strong> {data_fim}</p>
                    <p><strong>Local:</strong> {reuniao.sala_reuniao.nome}</p>
                    <p><strong>Organizador:</strong> {reuniao.criador.username}</p>
                </div>
                
                <div class="info-box">
                    <h3>👥 Participantes Convidados</h3>
                    <ul>
                        {''.join([f'<li>{p.username} ({p.email})</li>' for p in participantes])}
                    </ul>
                </div>
                
                <p>Por favor, confirme sua presença e anote em sua agenda.</p>
                
                <p>Atenciosamente,<br>
                <strong>Sistema de Agendamento de Reuniões</strong></p>
            </div>
            <div class="footer">
                <p>Este é um email automático. Não responda a esta mensagem.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Corpo em texto simples
    corpo_texto = f"""
    Olá!
    
    Uma nova reunião foi agendada e você foi convidado(a) para participar.
    
    DETALHES DA REUNIÃO:
    - Título: {reuniao.titulo}
    - Descrição: {reuniao.descricao or 'Sem descrição'}
    - Data e Hora de Início: {data_inicio}
    - Data e Hora de Término: {data_fim}
    - Local: {reuniao.sala_reuniao.nome}
    - Organizador: {reuniao.criador.username}
    
    PARTICIPANTES CONVIDADOS:
    {chr(10).join([f'- {p.username} ({p.email})' for p in participantes])}
    
    Por favor, confirme sua presença e anote em sua agenda.
    
    Atenciosamente,
    Sistema de Agendamento de Reuniões
    
    ---
    Este é um email automático. Não responda a esta mensagem.
    """
    
    # Enviar para todos os participantes
    emails_enviados = 0
    for participante in participantes:
        if enviar_email(participante.email, assunto, corpo_html, corpo_texto):
            emails_enviados += 1
    
    return emails_enviados

def enviar_notificacao_cancelamento(reuniao, participantes):
    """
    Envia notificação de cancelamento de reunião para todos os participantes
    """
    data_inicio = reuniao.data_inicio.strftime('%d/%m/%Y às %H:%M')
    data_fim = reuniao.data_fim.strftime('%d/%m/%Y às %H:%M')
    
    assunto = f"Reunião Cancelada: {reuniao.titulo}"
    
    # Template HTML do email
    corpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
            .info-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #dc3545; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>❌ Reunião Cancelada</h1>
            </div>
            <div class="content">
                <p>Olá!</p>
                
                <p>Informamos que a reunião abaixo foi <strong>cancelada</strong>.</p>
                
                <div class="info-box">
                    <h3>📋 Detalhes da Reunião Cancelada</h3>
                    <p><strong>Título:</strong> {reuniao.titulo}</p>
                    <p><strong>Descrição:</strong> {reuniao.descricao or 'Sem descrição'}</p>
                    <p><strong>Data e Hora de Início:</strong> {data_inicio}</p>
                    <p><strong>Data e Hora de Término:</strong> {data_fim}</p>
                    <p><strong>Local:</strong> {reuniao.sala_reuniao.nome}</p>
                    <p><strong>Organizador:</strong> {reuniao.criador.username}</p>
                </div>
                
                <div class="info-box">
                    <h3>👥 Participantes que Foram Notificados</h3>
                    <ul>
                        {''.join([f'<li>{p.username} ({p.email})</li>' for p in participantes])}
                    </ul>
                </div>
                
                <p>Por favor, remova este compromisso de sua agenda.</p>
                
                <p>Atenciosamente,<br>
                <strong>Sistema de Agendamento de Reuniões</strong></p>
            </div>
            <div class="footer">
                <p>Este é um email automático. Não responda a esta mensagem.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Corpo em texto simples
    corpo_texto = f"""
    Olá!
    
    Informamos que a reunião abaixo foi CANCELADA.
    
    DETALHES DA REUNIÃO CANCELADA:
    - Título: {reuniao.titulo}
    - Descrição: {reuniao.descricao or 'Sem descrição'}
    - Data e Hora de Início: {data_inicio}
    - Data e Hora de Término: {data_fim}
    - Local: {reuniao.sala_reuniao.nome}
    - Organizador: {reuniao.criador.username}
    
    PARTICIPANTES QUE FORAM NOTIFICADOS:
    {chr(10).join([f'- {p.username} ({p.email})' for p in participantes])}
    
    Por favor, remova este compromisso de sua agenda.
    
    Atenciosamente,
    Sistema de Agendamento de Reuniões
    
    ---
    Este é um email automático. Não responda a esta mensagem.
    """
    
    # Enviar para todos os participantes
    emails_enviados = 0
    for participante in participantes:
        if enviar_email(participante.email, assunto, corpo_html, corpo_texto):
            emails_enviados += 1
    
    return emails_enviados

