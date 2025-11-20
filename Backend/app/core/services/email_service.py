"""
Email Notification Service.
Sends email alerts for hot leads and system notifications.
"""
import logging
from typing import List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.core.models import Lead

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        """Initialize email service."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.enabled = all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password
        ])

        if not self.enabled:
            logger.warning("Email service not configured - notifications disabled")

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """
        Send email using configured SMTP server.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body_html: HTML body content
            body_text: Plain text body content (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Email not sent (service disabled): {subject}")
            return False

        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = ", ".join(to)
            message["Subject"] = subject

            # Add plain text version if provided
            if body_text:
                part1 = MIMEText(body_text, "plain")
                message.attach(part1)

            # Add HTML version
            part2 = MIMEText(body_html, "html")
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            logger.info(f"Email sent successfully to {', '.join(to)}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def notify_hot_lead(self, lead: Lead) -> bool:
        """
        Send notification for a hot lead.

        Args:
            lead: Hot lead to notify about

        Returns:
            bool: True if notification sent successfully
        """
        if not settings.NOTIFICATION_EMAILS:
            logger.info("No notification emails configured")
            return False

        subject = f"🔥 Nuevo Lead Caliente: {lead.name or 'Sin nombre'}"

        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: white; padding: 20px; border: 1px solid #e5e7eb; }}
                .lead-info {{ background: #f9fafb; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .lead-info-item {{ margin: 8px 0; }}
                .label {{ font-weight: bold; color: #6b7280; }}
                .value {{ color: #111827; }}
                .score {{ background: #DC2626; color: white; padding: 4px 12px; border-radius: 4px; display: inline-block; }}
                .cta {{ background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔥 Nuevo Lead Caliente</h1>
                    <p>Se ha capturado un lead de alta calidad</p>
                </div>
                <div class="content">
                    <div class="lead-info">
                        <div class="lead-info-item">
                            <span class="label">Nombre:</span>
                            <span class="value">{lead.name or 'No proporcionado'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Email:</span>
                            <span class="value">{lead.email or 'No proporcionado'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Teléfono:</span>
                            <span class="value">{lead.phone or 'No proporcionado'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Proyecto:</span>
                            <span class="value">{lead.project_type.value if lead.project_type else 'No especificado'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Presupuesto:</span>
                            <span class="value">{f'{int(lead.budget):,} EUR' if lead.budget else 'No proporcionado'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Timeline:</span>
                            <span class="value">{lead.timeline or 'No proporcionado'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Ubicación:</span>
                            <span class="value">{lead.location or 'No proporcionada'}</span>
                        </div>
                        <div class="lead-info-item">
                            <span class="label">Puntuación:</span>
                            <span class="score">{lead.score}/100</span>
                        </div>
                    </div>

                    <p><strong>Recomendación:</strong> Contacta con este lead lo antes posible. Los leads calientes tienen alta probabilidad de conversión.</p>

                    <a href="http://localhost:8000/admin/dashboard" class="cta">
                        Ver Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        🔥 Nuevo Lead Caliente Capturado

        Nombre: {lead.name or 'No proporcionado'}
        Email: {lead.email or 'No proporcionado'}
        Teléfono: {lead.phone or 'No proporcionado'}

        Proyecto: {lead.project_type.value if lead.project_type else 'No especificado'}
        Presupuesto: {f'{int(lead.budget):,} EUR' if lead.budget else 'No proporcionado'}
        Timeline: {lead.timeline or 'No proporcionado'}
        Ubicación: {lead.location or 'No proporcionada'}

        Puntuación: {lead.score}/100

        Recomendación: Contacta con este lead lo antes posible.
        Dashboard: http://localhost:8000/admin/dashboard
        """

        return await self.send_email(
            to=settings.NOTIFICATION_EMAILS,
            subject=subject,
            body_html=body_html,
            body_text=body_text
        )


# Global email service instance
email_service = EmailService()
