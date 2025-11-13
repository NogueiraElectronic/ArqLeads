"""
Message model - Represents individual chat messages.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    """
    Message model representing a single chat message.
    """
    
    __tablename__ = "messages"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Conversation Reference
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message Content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Metadata
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Flags
    is_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # AI Model Information
    model_used = Column(String(100), nullable=True)
    provider = Column(String(50), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"
    
    def is_user_message(self) -> bool:
        """Check if message is from user."""
        return self.role == MessageRole.USER
    
    def is_assistant_message(self) -> bool:
        """Check if message is from assistant."""
        return self.role == MessageRole.ASSISTANT
    
    def is_system_message(self) -> bool:
        """Check if message is a system message."""
        return self.role == MessageRole.SYSTEM
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role.value,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_error": self.is_error,
        }
    
    def to_chat_format(self) -> dict:
        """Convert message to chat completion format."""
        return {
            "role": self.role.value,
            "content": self.content
        }


class MessageTemplate:
    """Predefined message templates for the chatbot."""

    WELCOME = """Buenos días. Soy {bot_name}, asistente virtual de {studio_name}.

¿En qué tipo de proyecto de arquitectura estás trabajando?"""

    PROJECT_TYPE_OPTIONS = """Trabajamos en diversos tipos de proyectos:

- Vivienda unifamiliar: diseño de casa nueva o personalización
- Reforma de piso: renovación integral o parcial
- Obra nueva: construcción completa desde cero
- Rehabilitación: restauración y actualización de edificios
- Local comercial: diseño de espacios comerciales y oficinas
- Consulta técnica: asesoramiento profesional específico

¿Cuál describe mejor tu necesidad?"""

    BUDGET_QUESTION = """Entendido. En cuanto a {project_type}, me ayudaría conocer el rango de inversión que tienes previsto. Esto nos permitirá dimensionar correctamente el alcance y los acabados viables.

¿Has definido ya un presupuesto aproximado?"""

    TIMELINE_QUESTION = """Respecto al calendario del proyecto, ¿tienes una temporalidad definida?

- Próximos 3 meses: inicio inmediato
- Entre 3-6 meses: planificación media
- Entre 6-12 meses: planificación extendida
- Fase exploratoria: aún evaluando opciones

¿Cuál se ajusta mejor a tu situación?"""

    LOCATION_QUESTION = """¿En qué zona de {studio_location} se situaría el proyecto? La ubicación es relevante para evaluar aspectos de normativa local y accesibilidad."""

    CONTACT_REQUEST = """Gracias por la información compartida. El proyecto presenta características interesantes.

Para que un arquitecto del equipo pueda contactarte directamente y elaborar una propuesta detallada, necesitaré:

- Email de contacto
- Teléfono
- Nombre

¿Puedes facilitarme estos datos?"""

    HOT_LEAD_RESPONSE = """Perfecto, {name}. He registrado toda la información del proyecto.

Un arquitecto de {studio_name} se pondrá en contacto contigo en las próximas 24 horas laborables para:

- Analizar los detalles técnicos del proyecto
- Elaborar un presupuesto personalizado
- Resolver cualquier consulta técnica

¿Tienes preferencia de horario para la llamada?"""

    WARM_LEAD_RESPONSE = """Gracias por tu interés, {name}.

Hemos registrado la información del proyecto. Un arquitecto la revisará y te contactaremos próximamente para:

- Evaluar la viabilidad técnica
- Preparar un presupuesto orientativo
- Coordinar una reunión si procede

¿Hay algún detalle adicional sobre el proyecto que quieras mencionar?"""

    COLD_LEAD_RESPONSE = """Gracias por contactar con {studio_name}.

Entiendo que estás en fase inicial de evaluación. Te enviaremos información sobre nuestros servicios y algunos proyectos de referencia que puedan resultarte útiles.

Cuando tengas más definido el proyecto, estaremos disponibles para asesorarte.

¿Te interesaría recibir nuestro portfolio de proyectos ejecutados?"""

    GOODBYE = """Hasta pronto.

Si tienes más consultas sobre el proyecto, puedes volver a contactar cuando lo necesites.

{studio_name} - Arquitectura profesional"""

    ERROR = """Disculpa, he experimentado un error técnico.

¿Podrías repetir tu último mensaje?

Si el problema persiste, contacta directamente con el estudio:
Email: {contact_email}
Teléfono: {contact_phone}"""
    
    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """Format template with provided variables."""
        return template.format(**kwargs)