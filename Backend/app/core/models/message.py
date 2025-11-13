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
    
    WELCOME = """¡Hola! 👋 Soy {bot_name}, el asistente virtual de {studio_name}.

Estoy aquí para ayudarte con tu proyecto de arquitectura. ¿En qué tipo de proyecto estás pensando?"""
    
    PROJECT_TYPE_OPTIONS = """Puedo ayudarte con:

🏠 **Vivienda unifamiliar** - Casa nueva o proyecto personalizado
🏢 **Reforma de piso** - Renovación integral o parcial
🏗️ **Obra nueva** - Construcción desde cero
🔧 **Rehabilitación** - Restauración de edificios
🏪 **Local comercial** - Diseño de espacios comerciales
📋 **Consulta técnica** - Asesoramiento profesional

¿Cuál se ajusta más a lo que necesitas?"""
    
    BUDGET_QUESTION = """Perfecto, entiendo que estás interesado en {project_type}.

Para poder ayudarte mejor, ¿qué presupuesto aproximado tienes en mente? 
(No te preocupes, es solo para orientación inicial)"""
    
    TIMELINE_QUESTION = """Gracias por la información.

¿Cuándo te gustaría comenzar con el proyecto?

⚡ **En los próximos 3 meses**
📅 **Entre 3-6 meses**
🗓️ **Entre 6-12 meses**
💭 **Solo estoy explorando opciones**"""
    
    LOCATION_QUESTION = """¿En qué zona de {studio_location} sería el proyecto?"""
    
    CONTACT_REQUEST = """¡Excelente! Tu proyecto suena muy interesante.

Para que un arquitecto pueda contactarte y ofrecerte un presupuesto detallado, necesito algunos datos:

📧 **Email**
📱 **Teléfono**
👤 **Nombre**

¿Me los puedes facilitar?"""
    
    HOT_LEAD_RESPONSE = """¡Perfecto, {name}! 🎉

Tu proyecto es exactamente el tipo de trabajo que nos apasiona. Un arquitecto de {studio_name} se pondrá en contacto contigo en las **próximas 24 horas** para:

✅ Analizar tu proyecto en detalle
✅ Ofrecerte un presupuesto personalizado
✅ Resolver todas tus dudas

¿Cuál es el mejor horario para llamarte?"""
    
    WARM_LEAD_RESPONSE = """¡Gracias por tu interés, {name}! 😊

Hemos registrado tu proyecto y un arquitecto revisará la información. Te contactaremos próximamente para:

📋 Evaluar tu proyecto
💰 Preparar un presupuesto orientativo
📞 Coordinar una reunión

¿Hay algo más que quieras añadir sobre tu proyecto?"""
    
    COLD_LEAD_RESPONSE = """¡Gracias por contactar con {studio_name}! 😊

Entiendo que estás en fase de exploración. Te enviaremos información sobre nuestros servicios y proyectos realizados.

Cuando tengas más claro tu proyecto, ¡estaremos encantados de ayudarte!

¿Quieres que te enviemos nuestro portfolio?"""
    
    GOODBYE = """¡Hasta pronto! 👋

Si tienes más preguntas, no dudes en volver. Estaremos encantados de ayudarte.

{studio_name} - Tu proyecto, nuestra pasión."""
    
    ERROR = """Lo siento, he tenido un problema técnico. 😔

¿Podrías repetir tu mensaje?

Si el problema persiste, puedes contactarnos directamente en:
📧 {contact_email}
📱 {contact_phone}"""
    
    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """Format template with provided variables."""
        return template.format(**kwargs)