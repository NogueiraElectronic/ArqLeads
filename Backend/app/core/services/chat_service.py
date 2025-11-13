"""
Chat Service - Core AI conversation logic.
Handles AI provider integration and conversation flow management.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

from app.core.config import settings
from app.core.models import Lead, Conversation, Message, MessageRole, MessageTemplate, ProjectType

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing AI-powered chat conversations."""
    
    def __init__(self):
        """Initialize chat service with configured AI provider."""
        self.ai_config = settings.get_ai_config()
        self.provider = self.ai_config["provider"]
        
        # Initialize AI client based on provider
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.ai_config["api_key"])
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.ai_config["api_key"])
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")
        
        logger.info(f"ChatService initialized with provider: {self.provider}")
    
    def get_system_prompt(self) -> str:
        """Generate system prompt for the AI assistant."""
        return f"""Eres {settings.CHATBOT_NAME}, el asistente virtual de {settings.STUDIO_NAME}, 
un estudio de arquitectura profesional ubicado en {settings.STUDIO_LOCATION}.

PERSONALIDAD Y ESTILO:
- Eres {settings.CHATBOT_PERSONALITY}
- Usas un lenguaje claro, profesional pero cercano
- Respondes en español ({settings.CHATBOT_LANGUAGE})
- Eres empático y entiendes que hablar de proyectos de arquitectura puede ser abrumador
- Usas emojis ocasionalmente para dar calidez (pero sin excederte)

ESPECIALIDADES DEL ESTUDIO:
{', '.join(settings.studio_specialties_list)}

TU MISIÓN PRINCIPAL:
1. **Cualificar el lead** - Entender si es un cliente potencial real
2. **Recopilar información clave**:
   - Tipo de proyecto
   - Presupuesto aproximado
   - Timeline/urgencia
   - Ubicación del proyecto
   - Datos de contacto (nombre, email, teléfono)
3. **Mantener una conversación natural** - No parecer un formulario
4. **Generar interés** - Destacar la experiencia del estudio cuando sea relevante

REGLAS IMPORTANTES:
- NO inventes información sobre el estudio o proyectos que no conoces
- NO des presupuestos exactos (solo rangos muy generales si se pregunta)
- Si no sabes algo, di que un arquitecto le dará esa información
- Haz UNA pregunta a la vez (máximo dos relacionadas)
- Adapta tu lenguaje al del usuario (formal si es formal, casual si es casual)
- Si detectas un lead caliente (proyecto definido + presupuesto + urgencia), prioriza conseguir los datos de contacto

ESTRUCTURA DE CONVERSACIÓN IDEAL:
1. Saludo y pregunta sobre el proyecto
2. Entender el tipo de proyecto específico
3. Indagar sobre presupuesto (con tacto)
4. Preguntar por timeline
5. Ubicación del proyecto
6. Solicitar datos de contacto
7. Confirmar que el arquitecto contactará pronto

Recuerda: Tu objetivo es conseguir suficiente información para que un arquitecto real pueda hacer un seguimiento efectivo. ¡Sé útil, profesional y humano!"""
    
    async def generate_response(
        self,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> Tuple[str, int, int]:
        """Generate AI response based on conversation history."""
        start_time = datetime.now()
        
        try:
            # Prepare messages with system prompt
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ] + conversation_history
            
            # Add context if provided
            if context:
                context_msg = self._format_context(context)
                if context_msg:
                    messages.append({
                        "role": "system",
                        "content": f"Contexto adicional: {context_msg}"
                    })
            
            # Generate response based on provider
            if self.provider == "openai":
                response_text, tokens = await self._generate_openai(messages)
            elif self.provider == "anthropic":
                response_text, tokens = await self._generate_anthropic(messages)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return response_text, tokens, processing_time
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            raise
    
    async def _generate_openai(self, messages: List[Dict]) -> Tuple[str, int]:
        """Generate response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.ai_config["model"],
                messages=messages,
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"],
            )
            
            text = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            return text, tokens
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic(self, messages: List[Dict]) -> Tuple[str, int]:
        """Generate response using Anthropic API."""
        try:
            # Anthropic requires system prompt separately
            system_prompt = messages[0]["content"] if messages[0]["role"] == "system" else ""
            conv_messages = [m for m in messages if m["role"] != "system"]
            
            response = self.client.messages.create(
                model=self.ai_config["model"],
                max_tokens=self.ai_config["max_tokens"],
                system=system_prompt,
                messages=conv_messages
            )
            
            text = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens
            
            return text, tokens
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _format_context(self, context: Dict) -> str:
        """Format context dictionary into readable string."""
        parts = []
        
        if "project_type" in context:
            parts.append(f"Tipo de proyecto identificado: {context['project_type']}")
        
        if "budget_range" in context:
            parts.append(f"Rango de presupuesto: {context['budget_range']}")
        
        if "timeline" in context:
            parts.append(f"Timeline: {context['timeline']}")
        
        if "location" in context:
            parts.append(f"Ubicación: {context['location']}")
        
        return ". ".join(parts) if parts else ""
    
    def extract_information(self, message_text: str, lead: Lead) -> None:
        """Extract structured information from user message and update lead."""
        text_lower = message_text.lower()
        
        # Extract project type
        self._extract_project_type(text_lower, lead)
        
        # Extract budget
        self._extract_budget(message_text, lead)
        
        # Extract timeline
        self._extract_timeline(text_lower, lead)
        
        # Extract location
        self._extract_location(message_text, lead)
        
        # Extract contact info
        self._extract_contact_info(message_text, lead)
        
        # Update qualification flags
        lead.has_defined_project = lead.project_type is not None
        lead.has_budget = lead.budget is not None
        lead.has_timeline = lead.timeline is not None
        lead.has_location = lead.location is not None
        lead.contact_complete = all([lead.name, lead.email or lead.phone])
        
        # Recalculate score
        lead.score = lead.calculate_score()
        lead.update_category()
    
    def _extract_project_type(self, text: str, lead: Lead) -> None:
        """Extract project type from text."""
        keywords = {
            ProjectType.SINGLE_FAMILY: ["casa", "vivienda unifamiliar", "chalet", "villa"],
            ProjectType.APARTMENT_REFORM: ["piso", "apartamento", "reforma", "renovación"],
            ProjectType.NEW_CONSTRUCTION: ["obra nueva", "construcción", "construir"],
            ProjectType.REHABILITATION: ["rehabilitación", "restauración", "rehabilitar"],
            ProjectType.COMMERCIAL: ["local", "comercial", "negocio", "tienda", "oficina"],
            ProjectType.CONSULTATION: ["consulta", "asesoramiento", "información"],
        }
        
        for project_type, words in keywords.items():
            if any(word in text for word in words):
                lead.project_type = project_type
                break
    
    def _extract_budget(self, text: str, lead: Lead) -> None:
        """Extract budget from text using regex."""
        patterns = [
            # Con símbolos de moneda
            r'(\d{1,3}(?:[.,]\d{3})*)\s*[€$]',
            r'[€$]\s*(\d{1,3}(?:[.,]\d{3})*)',
            # Con palabras (euros, eur, dólares, etc.)
            r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:euros?|eur|dólares?|usd|dolares?)',
            # Con K (30k, 50K, etc.)
            r'(\d+)[kK]\s*(?:[€$]|euros?|eur)?',
            # Con "mil" (30 mil, 50 mil euros, etc.)
            r'(\d+)\s*mil\s*(?:[€$]|euros?|eur)?',
            # Solo números grandes (más de 1000, probablemente presupuesto)
            r'\b(\d{4,})\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    budget = float(budget_str)

                    # Aplicar multiplicadores
                    if re.search(r'\d+[kK]', text):
                        budget *= 1000
                    elif 'mil' in text.lower() and budget < 1000:
                        budget *= 1000

                    # Solo aceptar si parece un presupuesto razonable (500€ - 10M€)
                    if 500 <= budget <= 10_000_000:
                        lead.budget = budget
                        break
                except ValueError:
                    continue
    
    def _extract_timeline(self, text: str, lead: Lead) -> None:
        """Extract timeline from text."""
        timeline_patterns = {
            "inmediato": 1,
            "urgente": 1,
            "ya": 1,
            "1 mes": 1,
            "2 meses": 2,
            "3 meses": 3,
            "6 meses": 6,
            "1 año": 12,
            "este año": 6,
            "próximo año": 12,
        }
        
        for phrase, months in timeline_patterns.items():
            if phrase in text:
                lead.timeline = phrase
                lead.timeline_months = months
                break
    
    def _extract_location(self, text: str, lead: Lead) -> None:
        """Extract location from text."""
        locations = ["vigo", "pontevedra", "coruña", "ourense", "lugo", "santiago",
                    "ferrol", "baiona", "cangas", "porriño", "redondela"]
        
        for location in locations:
            if location in text:
                lead.location = location.capitalize()
                break
    
    def _extract_contact_info(self, text: str, lead: Lead) -> None:
        """Extract contact information from text."""
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            lead.email = email_match.group(0)
        
        # Extract phone
        phone_patterns = [
            r'\b([6-9]\d{8})\b',
            r'\b(\+34\s*[6-9]\d{8})\b',
            r'\b(34\s*[6-9]\d{8})\b',
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                lead.phone = phone_match.group(1)
                break
        
        # Extract name (basic)
        name_indicators = ["me llamo", "mi nombre es", "soy", "mi nombre:", "nombre:"]
        for indicator in name_indicators:
            if indicator in text.lower():
                parts = text.lower().split(indicator)
                if len(parts) > 1:
                    potential_name = parts[1].strip().split()[0:3]
                    lead.name = " ".join(potential_name).strip(',.;')
                    break
    
    def should_request_contact(self, lead: Lead) -> bool:
        """Determine if we should request contact information."""
        has_project_info = (
            lead.has_defined_project and
            (lead.has_budget or lead.has_timeline)
        )
        
        return (
            not lead.contact_complete and
            has_project_info and
            lead.score >= settings.SCORE_THRESHOLD_WARM
        )
    
    def get_next_question(self, lead: Lead, conversation: Conversation) -> Optional[str]:
        """Determine the next question to ask based on lead state."""
        if not lead.has_defined_project:
            return MessageTemplate.PROJECT_TYPE_OPTIONS
        
        if not lead.has_budget:
            return MessageTemplate.format(
                MessageTemplate.BUDGET_QUESTION,
                project_type=lead.project_type.value if lead.project_type else "tu proyecto"
            )
        
        if not lead.has_timeline:
            return MessageTemplate.TIMELINE_QUESTION
        
        if not lead.has_location:
            return MessageTemplate.format(
                MessageTemplate.LOCATION_QUESTION,
                studio_location=settings.STUDIO_LOCATION
            )
        
        if self.should_request_contact(lead):
            return MessageTemplate.CONTACT_REQUEST
        
        return None