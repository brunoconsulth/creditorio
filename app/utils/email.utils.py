import smtplib
from email.message import EmailMessage
from flask import current_app

def enviar_email_recuperacao(destinatario_email, link_redefinicao):
    msg = EmailMessage()
    msg['Subject'] = 'Recuperação de Senha'
    msg['From'] = 'seu_email@seudominio.com'
    msg['To'] = destinatario_email
    msg.set_content(f"""
Olá,

Recebemos uma solicitação para redefinir sua senha. Para continuar, clique no link abaixo:

{link_redefinicao}

Se você não solicitou a redefinição, ignore este e-mail.

Atenciosamente,
Equipe do Sistema
""")

    try:
        with smtplib.SMTP('smtp.seuprovedor.com', 587) as smtp:
            smtp.starttls()
            smtp.login('seu_email@seudominio.com', 'sua_senha')
            smtp.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail de recuperação: {e}")
