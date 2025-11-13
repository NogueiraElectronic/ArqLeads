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
        return f"""Eres {settings.CHATBOT_NAME}, el asistente virtual especializado de {settings.STUDIO_NAME},
un estudio de arquitectura profesional ubicado en {settings.STUDIO_LOCATION}.

━━━ PERSONALIDAD Y ESTILO ━━━
- Eres {settings.CHATBOT_PERSONALITY}
- Tu comunicación es profesional pero cálida y accesible
- Respondes en español (es-ES)
- Eres empático: entiendes que cada proyecto es único e importante
- Usas emojis ocasionalmente (máximo 1-2 por mensaje) solo cuando aporten valor
- Eres consultivo, no transaccional

━━━ ESPECIALIDADES DEL ESTUDIO ━━━
{', '.join(settings.studio_specialties_list)}

━━━ TU MISIÓN ━━━
1. **Comprender verdaderamente el proyecto del cliente**
   - Qué quiere lograr, no solo qué quiere construir
   - Sus motivaciones y preocupaciones

2. **Recopilar información estratégica naturalmente**:
   ✓ Tipo de proyecto específico
   ✓ Presupuesto orientativo (sin presionar)
   ✓ Timeline y urgencia
   ✓ Ubicación del proyecto
   ✓ Datos de contacto (cuando esté cualificado)

3. **Generar confianza**:
   - Demuestra experiencia sin ser pretencioso
   - Ofrece valor en cada interacción
   - Sé honesto sobre lo que sabes y lo que no

━━━ REGLAS CRÍTICAS ━━━
✗ NUNCA inventes datos del estudio, proyectos o precios
✗ NUNCA des presupuestos exactos (usa rangos generales solo si preguntan directamente)
✗ NUNCA hagas más de 2 preguntas seguidas sin aportar valor
✗ NUNCA repitas la misma pregunta si el usuario ya respondió algo relacionado
✗ NUNCA seas robótico o parezca un formulario

✓ SI detectas información en sus respuestas, reconócelo
✓ SI el usuario da detalles extra, muestra interés genuino
✓ SI no entiendes algo, pide aclaración de forma natural
✓ SI el lead parece caliente (proyecto + presupuesto + urgencia), prioriza contacto
✓ SI el usuario pregunta algo técnico, sé honesto y ofrece que un arquitecto le responda

━━━ FLUJO CONVERSACIONAL INTELIGENTE ━━━
NO sigas un script rígido. Adapta según lo que el usuario dice:

**Lead Frío** (explorando):
→ Comparte información útil, ayuda a clarificar ideas, construye relación

**Lead Tibio** (proyecto definido):
→ Profundiza en detalles, valida viabilidad, explora timeline

**Lead Caliente** (proyecto + presupuesto + urgencia):
→ Prioriza obtener contacto, confirma next steps, genera expectativa de llamada

━━━ EJEMPLOS DE RESPUESTAS EXCELENTES ━━━

❌ MAL: "Perfecto. ¿Cuál es tu presupuesto?"
✓ BIEN: "Una reforma de baño puede variar bastante según los acabados. Para darte una orientación más precisa, ¿tienes en mente un presupuesto aproximado? Así sabré qué opciones se ajustan mejor a ti."

❌ MAL: "¿En qué zona está el proyecto?"
✓ BIEN: "¿En qué zona de {settings.STUDIO_LOCATION} sería el proyecto? A veces los detalles de ubicación influyen en aspectos técnicos como normativa o accesos."

❌ MAL (repitiendo pregunta): "¿Cuándo quieres empezar?"
✓ BIEN (reconociendo respuesta): "Entiendo que estás explorando opciones aún. Perfecto, no hay prisa. ¿La ubicación del proyecto sería en {settings.STUDIO_LOCATION} o alrededores?"

━━━ CONTEXTO DE EXTRACCIÓN ━━━
El sistema intentará extraer automáticamente datos estructurados de las conversaciones.
TU trabajo es que la conversación fluya naturalmente mientras recopilas información.
Si el usuario da información vaga, está bien - no fuerces. Construye confianza primero.

Recuerda: Cada conversación es una oportunidad de demostrar profesionalismo y ayudar a alguien a materializar su proyecto. ¡Hazlo memorable!"""
    
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
        """Format context dictionary into readable string for AI."""
        if not context:
            return ""

        parts = []

        # Información del lead ya capturada
        if context.get("project_type"):
            parts.append(f"✓ Proyecto identificado: {context['project_type']}")

        if context.get("budget"):
            budget = context['budget']
            if budget >= 1000:
                budget_str = f"{int(budget/1000)}k€" if budget >= 1000 else f"{int(budget)}€"
            else:
                budget_str = f"{int(budget)}€"
            parts.append(f"✓ Presupuesto capturado: {budget_str}")

        if context.get("timeline"):
            parts.append(f"✓ Timeline capturado: {context['timeline']}")

        if context.get("location"):
            parts.append(f"✓ Ubicación capturada: {context['location']}")

        if context.get("name"):
            parts.append(f"✓ Nombre capturado: {context['name']}")

        if context.get("email") or context.get("phone"):
            contact_methods = []
            if context.get("email"):
                contact_methods.append("email")
            if context.get("phone"):
                contact_methods.append("teléfono")
            parts.append(f"✓ Contacto capturado: {', '.join(contact_methods)}")

        # Información sobre qué falta
        missing = []
        if not context.get("budget"):
            missing.append("presupuesto")
        if not context.get("timeline"):
            missing.append("timeline")
        if not context.get("location"):
            missing.append("ubicación")
        if not context.get("email") and not context.get("phone"):
            missing.append("contacto")

        if missing:
            parts.append(f"⚠ Falta capturar: {', '.join(missing)}")

        # Score del lead
        if context.get("lead_score"):
            score = context["lead_score"]
            category = context.get("lead_category", "unknown")
            parts.append(f"📊 Score actual: {score}/100 ({category})")

        result = "\n".join(parts) if parts else ""

        if result:
            return f"\n━━━ CONTEXTO DEL LEAD ━━━\n{result}\n━━━━━━━━━━━━━━━━━━━━━━\n\nBASANDOTE EN ESTE CONTEXTO, continúa la conversación de forma natural. Si ya tienes información capturada, NO la vuelvas a preguntar."

        return ""
    
    def extract_information(self, message_text: str, lead: Lead) -> None:
        """Extract structured information from user message and update lead."""
        text_lower = message_text.lower()

        # Guardar valores anteriores para detectar cambios
        old_budget = lead.budget
        old_timeline = lead.timeline
        old_location = lead.location

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

        # Log what was extracted for debugging
        if lead.budget != old_budget:
            logger.info(f"Extracted budget: {lead.budget}")
        if lead.timeline != old_timeline:
            logger.info(f"Extracted timeline: {lead.timeline}")
        if lead.location != old_location:
            logger.info(f"Extracted location: {lead.location}")
    
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
        """Extract timeline from text using flexible pattern matching."""
        text_lower = text.lower()

        # Patrones más flexibles con regex
        timeline_rules = [
            # Inmediato/urgente
            (r'\b(inmediato|urgente|ya|ahora|cuanto antes)\b', "inmediato", 1),
            # Meses específicos
            (r'\b(?:en\s+)?(?:los?\s+)?(?:próximos?\s+)?([1-3])\s*mes(?:es)?\b', None, None),  # 1-3 meses
            (r'\b(?:en\s+)?(?:los?\s+)?(?:próximos?\s+)?([4-6])\s*mes(?:es)?\b', None, None),  # 4-6 meses
            (r'\b(?:en\s+)?(?:los?\s+)?(?:próximos?\s+)?([7-9]|1[0-2])\s*mes(?:es)?\b', None, None),  # 7-12 meses
            # Rangos de meses
            (r'\b(?:entre\s+)?3\s*-?\s*6\s*mes(?:es)?\b', "3-6 meses", 4),
            (r'\b(?:entre\s+)?6\s*-?\s*12\s*mes(?:es)?\b', "6-12 meses", 9),
            # Años
            (r'\b(?:en\s+)?(?:un\s+)?(?:1\s+)?año\b', "1 año", 12),
            (r'\b(?:el\s+)?(?:este\s+)?año\b', "este año", 6),
            (r'\b(?:el\s+)?(?:próximo|siguiente)\s+año\b', "próximo año", 12),
            # Opciones del menú del bot
            (r'explor(?:ando|ar)\s+(?:las?\s+)?opcion(?:es)?', "explorando opciones", 12),
            (r'solo\s+(?:estoy\s+)?explor', "explorando opciones", 12),
            (r'no\s+(?:tengo\s+)?prisa', "sin prisa", 12),
            # Respuestas tipo "4" cuando hay opciones de menú
            (r'^\s*[4]\s*$', "explorando opciones", 12),
            (r'^\s*[1]\s*$', "3 meses", 3),
            (r'^\s*[2]\s*$', "3-6 meses", 4),
            (r'^\s*[3]\s*$', "6-12 meses", 9),
        ]

        for pattern, label, months in timeline_rules:
            match = re.search(pattern, text_lower)
            if match:
                # Si el patrón captura un grupo (número de meses), úsalo
                if match.groups() and match.group(1).isdigit():
                    months_num = int(match.group(1))
                    lead.timeline = f"{months_num} meses"
                    lead.timeline_months = months_num
                else:
                    lead.timeline = label
                    lead.timeline_months = months
                break
    
    def _extract_location(self, text: str, lead: Lead) -> None:
        """Extract location from text with flexible matching."""
        text_lower = text.lower()

        # Ciudades principales de Galicia
        main_cities = {
            "vigo": ["vigo", "vigués", "viguesa"],
            "pontevedra": ["pontevedra", "pontevedrés"],
            "coruña": ["coruña", "a coruña", "la coruña", "corunés"],
            "ourense": ["ourense", "orense", "ourensán"],
            "lugo": ["lugo", "lugués"],
            "santiago": ["santiago", "compostela", "compostelano"],
            "ferrol": ["ferrol", "ferrolano"],
        }

        # Barrios y zonas de Vigo (más común en arquitectura)
        vigo_zones = [
            "urzaiz", "coia", "samil", "bouzas", "teis", "centro", "calvario",
            "travesia", "castrelos", "beade", "coruxo", "oia", "navia",
            "candeán", "cabral", "lavadores", "alcabre", "matama"
        ]

        # Otras localidades gallegas
        other_locations = [
            "baiona", "cangas", "porriño", "redondela", "moaña", "nigrán",
            "gondomar", "mos", "soutomaior", "vilaboa"
        ]

        # 1. Buscar ciudades principales
        for city, variations in main_cities.items():
            for variation in variations:
                if variation in text_lower:
                    lead.location = city.capitalize()
                    return

        # 2. Buscar barrios de Vigo (si menciona un barrio, asumimos Vigo)
        for zone in vigo_zones:
            if zone in text_lower:
                lead.location = f"Vigo - {zone.capitalize()}"
                return

        # 3. Buscar otras localidades
        for location in other_locations:
            if location in text_lower:
                lead.location = location.capitalize()
                return

        # 4. Detectar si menciona "aquí", "mi ciudad", etc. (guardar el texto original)
        generic_locations = ["aquí", "mi ciudad", "donde vivo", "mi zona"]
        for generic in generic_locations:
            if generic in text_lower:
                lead.location = "Por confirmar"
                return

        # 5. Si contiene "avenida", "calle", "rúa", probablemente es una dirección
        if any(word in text_lower for word in ["avenida", "calle", "rúa", "rua", "plaza"]):
            # Extraer parte de la dirección para guardarla
            lead.location = text[:100]  # Guardar primeros 100 caracteres
            return
    
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