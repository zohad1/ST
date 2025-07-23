# app/services/email_service.py - Enhanced Email Service with Gmail/Mailgun Support
import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import ssl
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration from settings
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.MAIL_FROM
        self.from_name = settings.MAIL_FROM_NAME
        self.use_tls = settings.SMTP_TLS
        
        # Mailgun configuration (optional)
        self.mailgun_api_key = getattr(settings, 'MAILGUN_API_KEY', None)
        self.mailgun_domain = getattr(settings, 'MAILGUN_DOMAIN', None)
        self.mailgun_url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages" if self.mailgun_domain else None
        
        # Frontend URL for email links
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Log configuration (without password)
        logger.info(f"Email Service Configuration:")
        logger.info(f"  SMTP Server: {self.smtp_server}")
        logger.info(f"  SMTP Port: {self.smtp_port}")
        logger.info(f"  Username: {self.username}")
        logger.info(f"  From Email: {self.from_email}")
        logger.info(f"  Use TLS: {self.use_tls}")
        logger.info(f"  Password configured: {'Yes' if self.password else 'No'}")
        logger.info(f"  Mailgun API Key: {'Yes' if self.mailgun_api_key else 'No'}")
        logger.info(f"  Mailgun Domain: {self.mailgun_domain}")
        logger.info(f"  Frontend URL: {self.frontend_url}")
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using Mailgun (preferred) or SMTP fallback"""
        
        # Try Mailgun first if configured
        if self.mailgun_api_key and self.mailgun_domain:
            return self._send_via_mailgun(to_email, subject, html_content, text_content)
        
        # Fallback to SMTP (Gmail)
        return self._send_via_smtp(to_email, subject, html_content, text_content)
    
    def _send_via_mailgun(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email via Mailgun API"""
        try:
            logger.info(f"📧 Sending email via Mailgun to: {to_email}")
            logger.info(f"   Subject: {subject}")
            
            data = {
                'from': f"{self.from_name} <{self.from_email}>",
                'to': to_email,
                'subject': subject,
                'html': html_content
            }
            
            if text_content:
                data['text'] = text_content
            
            response = requests.post(
                self.mailgun_url,
                auth=("api", self.mailgun_api_key),
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email sent successfully via Mailgun to: {to_email}")
                return True
            else:
                logger.error(f"❌ Mailgun API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mailgun error: {str(e)}")
            return False
    
    def _send_via_smtp(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using SMTP (Gmail) with detailed logging"""
        try:
            logger.info(f"📧 Sending email via SMTP to: {to_email}")
            logger.info(f"   Subject: {subject}")
            
            # Check if email is enabled
            if not settings.MAIL_ENABLED:
                logger.warning("❌ Email sending is disabled in settings")
                return False
            
            # Check if password is configured
            if not self.password:
                logger.error("❌ SMTP password not configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Connect to server and send email
            logger.info(f"📧 Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            
            if self.smtp_port == 465:
                # SSL connection
                logger.info("   Using SSL connection")
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    logger.info("   Logging in...")
                    server.login(self.username, self.password)
                    logger.info("   Sending email...")
                    server.sendmail(self.from_email, to_email, message.as_string())
            else:
                # STARTTLS connection
                logger.info("   Using STARTTLS connection")
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        logger.info("   Starting TLS...")
                        server.starttls()
                    logger.info("   Logging in...")
                    server.login(self.username, self.password)
                    logger.info("   Sending email...")
                    server.sendmail(self.from_email, to_email, message.as_string())
                
            logger.info(f"✅ Email sent successfully via SMTP to: {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed: {str(e)}")
            logger.error("   Check your email username and password")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"❌ Failed to connect to SMTP server: {str(e)}")
            logger.error(f"   Check server: {self.smtp_server} and port: {self.smtp_port}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email: {str(e)}")
            logger.error(f"   Error type: {type(e).__name__}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _create_verification_email(self, username: str, verification_url: str, fallback_url: str = None) -> tuple[str, str]:
        """Create verification email with LaunchPaid branding"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #000000; color: #ffffff; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111827; padding: 30px; border-radius: 10px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 28px; font-weight: bold; color: #9333ea; margin-bottom: 10px; }}
                .title {{ font-size: 24px; color: #ffffff; margin-bottom: 20px; }}
                .content {{ color: #9ca3af; margin-bottom: 30px; }}
                .button {{ display: inline-block; background: #9333ea; color: #ffffff !important; font-weight: bold; padding: 14px 32px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-size: 16px; text-align: center; min-width: 200px; box-shadow: 0 4px 6px rgba(147, 51, 234, 0.3); }}
                .button:hover {{ background: #7c3aed; color: #ffffff !important; box-shadow: 0 6px 8px rgba(147, 51, 234, 0.4); }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #374151; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚀 LaunchPAID</div>
                    <h1 class="title">Verify Your Email Address</h1>
                </div>
                
                <div class="content">
                    <p>Hi {username},</p>
                    
                    <p>Welcome to LaunchPAID! To complete your account setup, please verify your email address.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </div>
                    
                    {f'<p>If the button above does not work, <a href="{fallback_url}" style="color: #9333ea;">click here</a>.</p>' if fallback_url else ''}
                    
                    <p>This verification link will expire in 24 hours.</p>
                    
                    <p>If you didn't create a LaunchPAID account, you can safely ignore this email.</p>
                </div>
                
                <div class="footer">
                    <p>Best regards,<br>The LaunchPAID Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {username},
        
        Welcome to LaunchPAID! To complete your account setup, please verify your email address.
        
        Click this link to verify: {verification_url}
        
        {f'If the link above does not work, try: {fallback_url}' if fallback_url else ''}
        
        This verification link will expire in 24 hours.
        
        If you didn't create a LaunchPAID account, you can safely ignore this email.
        
        Best regards,
        The LaunchPAID Team
        """
        
        return html_content, text_content
    
    def _create_password_reset_email(self, username: str, reset_url: str, fallback_url: str = None) -> tuple[str, str]:
        """Create password reset email with LaunchPaid branding"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #000000; color: #ffffff; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111827; padding: 30px; border-radius: 10px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 28px; font-weight: bold; color: #dc2626; margin-bottom: 10px; }}
                .title {{ font-size: 24px; color: #ffffff; margin-bottom: 20px; }}
                .content {{ color: #9ca3af; margin-bottom: 30px; }}
                .button {{ display: inline-block; background: #dc2626; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .button:hover {{ background: #b91c1c; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #374151; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔐 LaunchPAID</div>
                    <h1 class="title">Reset Your Password</h1>
                </div>
                
                <div class="content">
                    <p>Hi {username},</p>
                    
                    <p>We received a request to reset your password for your LaunchPAID account.</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </div>
                    
                    {f'<p>If the button above does not work, <a href="{fallback_url}" style="color: #dc2626;">click here</a>.</p>' if fallback_url else ''}
                    
                    <p>This password reset link will expire in 1 hour for security reasons.</p>
                    
                    <p>If you didn't request a password reset, please ignore this email.</p>
                </div>
                
                <div class="footer">
                    <p>Best regards,<br>The LaunchPAID Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {username},
        
        We received a request to reset your password for your LaunchPAID account.
        
        Click this link to reset your password: {reset_url}
        
        {f'If the link above does not work, try: {fallback_url}' if fallback_url else ''}
        
        This password reset link will expire in 1 hour for security reasons.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        The LaunchPAID Team
        """
        
        return html_content, text_content
    
    def _create_welcome_email(self, username: str, user_role: str, dashboard_url: str) -> tuple[str, str]:
        """Create welcome email with LaunchPaid branding"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to LaunchPAID</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #000000; color: #ffffff; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111827; padding: 30px; border-radius: 10px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 28px; font-weight: bold; color: #9333ea; margin-bottom: 10px; }}
                .title {{ font-size: 24px; color: #ffffff; margin-bottom: 20px; }}
                .content {{ color: #9ca3af; margin-bottom: 30px; }}
                .button {{ display: inline-block; background: #9333ea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .button:hover {{ background: #7c3aed; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #374151; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎉 LaunchPAID</div>
                    <h1 class="title">Welcome to LaunchPAID!</h1>
                </div>
                
                <div class="content">
                    <p>Hi {username},</p>
                    
                    <p>Welcome to LaunchPAID! Your account has been successfully verified.</p>
                    
                    <div style="text-align: center;">
                        <a href="{dashboard_url}" class="button">Access Your Dashboard</a>
                    </div>
                    
                    <p>We're excited to have you on board and can't wait to see what you'll accomplish!</p>
                </div>
                
                <div class="footer">
                    <p>Best regards,<br>The LaunchPAID Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {username},
        
        Welcome to LaunchPAID! Your account has been successfully verified.
        
        Access your dashboard: {dashboard_url}
        
        We're excited to have you on board and can't wait to see what you'll accomplish!
        
        Best regards,
        The LaunchPAID Team
        """
        
        return html_content, text_content

    # ---------------------------------------------------------------
    # Login notification email
    # ---------------------------------------------------------------
    def _create_login_notification_email(self, username: str, login_time: str, ip_address: str, user_agent: str, dashboard_url: str) -> tuple[str, str]:
        """Create login notification email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Login Detected</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #000000; color: #ffffff; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111827; padding: 30px; border-radius: 10px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 28px; font-weight: bold; color: #10b981; margin-bottom: 10px; }}
                .title {{ font-size: 24px; color: #ffffff; margin-bottom: 20px; }}
                .content {{ color: #9ca3af; margin-bottom: 30px; }}
                .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .button:hover {{ background: #059669; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #374151; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔔 LaunchPAID</div>
                    <h1 class="title">New Login Detected</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your LaunchPAID account was just accessed.</p>
                    <ul>
                        <li><strong>Time:</strong> {login_time}</li>
                        <li><strong>IP Address:</strong> {ip_address}</li>
                        <li><strong>Device:</strong> {user_agent}</li>
                    </ul>
                    <p>If this was you, no further action is required. If you don’t recognize this activity, we recommend changing your password immediately.</p>
                    <div style="text-align: center;">
                        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                    </div>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LaunchPAID Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = (
            f"Hi {username},\n\n"
            "Your LaunchPAID account was just accessed.\n\n"
            f"Time: {login_time}\nIP Address: {ip_address}\nDevice: {user_agent}\n\n"
            "If this was you, no action is needed. If not, please reset your password."
        )
        return html_content, text_content

    def send_login_notification_email(self, to_email: str, username: str, ip_address: str, user_agent: str) -> bool:
        """Send login notification email"""
        login_time = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        dashboard_url = f"{self.frontend_url}/creator-dashboard"  # generic dashboard
        subject = "New Login to Your LaunchPAID Account"

        html_content, text_content = self._create_login_notification_email(
            username, login_time, ip_address, user_agent, dashboard_url
        )
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_verification_email(self, to_email: str, username: str, verification_token: str) -> bool:
        """Send email verification email using our templates"""
        
        logger.info(f"📧 Preparing verification email for: {to_email}")
        logger.info(f"   Username: {username}")
        logger.info(f"   Token: {verification_token[:8]}...")
        
        verification_url = f"{self.frontend_url}/auth/signup/verification?token={verification_token}&email={to_email}"
        fallback_url = f"{self.frontend_url}/auth/signup/verification?token={verification_token}"
        
        subject = "Verify Your Email - LaunchPAID"
        
        # Create email using our templates
        html_content, text_content = self._create_verification_email(username, verification_url, fallback_url)
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_token: str) -> bool:
        """Send password reset email using our templates"""
        
        logger.info(f"📧 Preparing password reset email for: {to_email}")
        logger.info(f"   Username: {username}")
        logger.info(f"   Token: {reset_token[:8]}...")
        
        reset_url = f"{self.frontend_url}/auth/forgot-password?token={reset_token}&email={to_email}"
        fallback_url = f"{self.frontend_url}/auth/forgot-password?token={reset_token}"
        
        subject = "Reset Your Password - LaunchPAID"
        
        # Create email using our templates
        html_content, text_content = self._create_password_reset_email(username, reset_url, fallback_url)
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(self, to_email: str, username: str, user_role: str) -> bool:
        """Send welcome email after successful verification"""
        
        logger.info(f"📧 Preparing welcome email for: {to_email}")
        logger.info(f"   Username: {username}")
        logger.info(f"   Role: {user_role}")
        
        dashboard_url = f"{self.frontend_url}/dashboard"
        
        subject = "Welcome to LaunchPAID!"
        
        # Create email using our templates
        html_content, text_content = self._create_welcome_email(username, user_role, dashboard_url)
        
        return self.send_email(to_email, subject, html_content, text_content)

# Create global instance
email_service = EmailService()