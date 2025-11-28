"""
Servicio de envío de correos electrónicos
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de email
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Envía un correo electrónico
    
    Args:
        to_email: Dirección de destino
        subject: Asunto del correo
        html_content: Contenido HTML del correo
        
    Returns:
        True si se envió correctamente, False si hubo error
    """
    try:
        # Crear mensaje
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        
        # Agregar contenido HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Conectar y enviar
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, message.as_string())
        
        print(f"✅ Correo enviado a {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando correo a {to_email}: {str(e)}")
        return False


def send_confirmation_email(email: str, nombre: str, token: str) -> bool:
    """
    Envía correo de confirmación de cuenta
    """
    confirmation_url = f"{FRONTEND_URL}/auth/confirmar-correo/{token}"
    
    subject = "Confirma tu cuenta en Performia"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .button {{
                display: inline-block;
                background: #1e3a5f;
                color: white !important;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 12px;
                border-radius: 0 0 10px 10px;
                background: #f0f0f0;
            }}
            .token {{
                background: #e8e8e8;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                word-break: break-all;
                font-size: 12px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Performia</h1>
            <p>Sistema de Evaluación de Desempeño</p>
        </div>
        <div class="content">
            <h2>¡Hola {nombre}!</h2>
            <p>Gracias por registrarte en <strong>Performia</strong>. Para completar tu registro y activar tu cuenta, por favor confirma tu dirección de correo electrónico.</p>
            
            <p style="text-align: center;">
                <a href="{confirmation_url}" class="button">Confirmar mi correo</a>
            </p>
            
            <p>Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
            <div class="token">{confirmation_url}</div>
            
            <p><strong>Este enlace expirará en 24 horas.</strong></p>
            
            <p>Si no creaste esta cuenta, puedes ignorar este correo.</p>
        </div>
        <div class="footer">
            <p>© 2025 Performia - Sistema de Evaluación de Desempeño</p>
            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)


def send_password_reset_email(email: str, nombre: str, token: str) -> bool:
    """
    Envía correo para restablecer contraseña (con enlace)
    """
    reset_url = f"{FRONTEND_URL}/auth/reset-password/{token}"
    
    subject = "Restablece tu contraseña en Performia"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .button {{
                display: inline-block;
                background: #dc3545;
                color: white !important;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 12px;
                background: #f0f0f0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Performia</h1>
            <p>Sistema de Evaluación de Desempeño</p>
        </div>
        <div class="content">
            <h2>Hola {nombre},</h2>
            <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
            
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Restablecer Contraseña</a>
            </p>
            
            <p><strong>Este enlace expirará en 1 hora.</strong></p>
            
            <p>Si no solicitaste este cambio, ignora este correo.</p>
        </div>
        <div class="footer">
            <p>© 2025 Performia - Sistema de Evaluación de Desempeño</p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)


def send_password_reset_code_email(email: str, nombre: str, codigo: str) -> bool:
    """
    Envía correo con código de 6 dígitos para recuperación de contraseña
    """
    subject = "Código de recuperación - Performia"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
                text-align: center;
            }}
            .code {{
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 10px;
                text-align: center;
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                color: white;
                padding: 25px 40px;
                border-radius: 10px;
                margin: 25px 0;
                display: inline-block;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 12px;
                background: #f0f0f0;
                border-radius: 0 0 10px 10px;
            }}
            .warning {{
                background: #fff3cd;
                border: 1px solid #ffc107;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Performia</h1>
            <p>Recuperación de Contraseña</p>
        </div>
        <div class="content">
            <h2>Hola {nombre},</h2>
            <p>Recibimos una solicitud para restablecer tu contraseña.</p>
            <p>Tu código de verificación es:</p>
            
            <div class="code">{codigo}</div>
            
            <div class="warning">
                <strong>⏱️ Este código expirará en 15 minutos.</strong>
            </div>
            
            <p>Ingresa este código en la aplicación para continuar.</p>
            
            <p style="color: #666; font-size: 14px;">Si no solicitaste este cambio, ignora este correo.</p>
        </div>
        <div class="footer">
            <p>© 2025 Performia - Sistema de Evaluación de Desempeño</p>
            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)