"""
Tests for chat service - lead extraction and AI integration.
"""
import pytest
from app.core.services.chat_service import ChatService
from app.core.models import Lead, ProjectType


class TestLeadExtraction:
    """Test automatic lead information extraction."""

    def test_extract_budget_with_euros(self):
        """Test budget extraction with 'euros' keyword."""
        service = ChatService()
        lead = Lead()

        service._extract_budget("Mi presupuesto es de 20000 euros", lead)

        assert lead.budget == 20000.0

    def test_extract_budget_with_k_format(self):
        """Test budget extraction with K format (20k)."""
        service = ChatService()
        lead = Lead()

        service._extract_budget("Tengo unos 25k disponibles", lead)

        assert lead.budget == 25000.0

    def test_extract_budget_with_currency_symbol(self):
        """Test budget extraction with currency symbol."""
        service = ChatService()
        lead = Lead()

        service._extract_budget("€15000 aproximadamente", lead)

        assert lead.budget == 15000.0

    def test_extract_timeline_months(self):
        """Test timeline extraction with months."""
        service = ChatService()
        lead = Lead()

        service._extract_timeline("en 3 meses", lead)

        assert lead.timeline == "3 meses"
        assert lead.timeline_months == 3

    def test_extract_timeline_inmediato(self):
        """Test timeline extraction for immediate projects."""
        service = ChatService()
        lead = Lead()

        service._extract_timeline("cuanto antes, es urgente", lead)

        assert lead.timeline == "inmediato"
        assert lead.timeline_months == 1

    def test_extract_project_type_reforma(self):
        """Test project type extraction for apartment reform."""
        service = ChatService()
        lead = Lead()

        service._extract_project_type("quiero reformar mi piso", lead)

        assert lead.project_type == ProjectType.APARTMENT_REFORM

    def test_extract_project_type_casa(self):
        """Test project type extraction for single family house."""
        service = ChatService()
        lead = Lead()

        service._extract_project_type("construcción de una casa", lead)

        assert lead.project_type == ProjectType.SINGLE_FAMILY

    def test_extract_location_vigo(self):
        """Test location extraction for Vigo."""
        service = ChatService()
        lead = Lead()

        service._extract_location("está en vigo centro", lead)

        assert "vigo" in lead.location.lower()

    def test_extract_email(self):
        """Test email extraction."""
        service = ChatService()
        lead = Lead()

        service._extract_contact_info("mi email es juan@example.com", lead)

        assert lead.email == "juan@example.com"

    def test_extract_phone_spanish_format(self):
        """Test phone extraction in Spanish format."""
        service = ChatService()
        lead = Lead()

        service._extract_contact_info("llámame al 666777888", lead)

        assert lead.phone == "+34666777888"

    def test_lead_score_calculation(self):
        """Test lead score calculation."""
        lead = Lead()
        lead.project_type = ProjectType.APARTMENT_REFORM
        lead.budget = 25000.0
        lead.timeline = "3 meses"
        lead.timeline_months = 3
        lead.location = "Vigo"

        score = lead.calculate_score()

        assert score >= 60  # Should be warm lead
        assert score <= 80

    def test_lead_category_hot(self):
        """Test lead categorization as HOT."""
        lead = Lead()
        lead.project_type = ProjectType.APARTMENT_REFORM
        lead.budget = 50000.0
        lead.timeline = "inmediato"
        lead.timeline_months = 1
        lead.location = "Vigo"
        lead.name = "Juan"
        lead.email = "juan@example.com"

        lead.score = lead.calculate_score()
        lead.update_category()

        assert lead.score >= 70
        assert lead.category.value == "hot"


class TestChatServiceIntegration:
    """Test chat service integration with AI providers."""

    @pytest.mark.asyncio
    async def test_system_prompt_generation(self):
        """Test that system prompt is generated correctly."""
        service = ChatService()

        prompt = service.get_system_prompt()

        assert "AsistenteArq" in prompt
        assert "Vigo" in prompt
        assert "PROHIBIDO: Usar emojis" in prompt
        assert "MÁXIMO 2-3 líneas" in prompt

    def test_format_context_with_lead_info(self):
        """Test context formatting for AI."""
        service = ChatService()
        context = {
            "project_type": "APARTMENT_REFORM",
            "budget": 20000,
            "timeline": "3 meses",
            "location": "Vigo",
            "lead_score": 65,
            "lead_category": "warm"
        }

        formatted = service._format_context(context)

        assert "[CAPTURADO]" in formatted
        assert "20k EUR" in formatted or "20000" in formatted
        assert "warm" in formatted.lower()


class TestValidation:
    """Test input validation and sanitization."""

    def test_extract_budget_ignores_small_numbers(self):
        """Test that small numbers are not extracted as budget."""
        service = ChatService()
        lead = Lead()

        service._extract_budget("tengo 2 baños", lead)

        assert lead.budget is None  # Should not extract "2" as budget

    def test_extract_budget_ignores_unrealistic_values(self):
        """Test that unrealistic budgets are ignored."""
        service = ChatService()
        lead = Lead()

        service._extract_budget("50 euros", lead)  # Too small

        assert lead.budget is None

    def test_extract_email_validates_format(self):
        """Test that invalid emails are not extracted."""
        service = ChatService()
        lead = Lead()

        service._extract_contact_info("email invalido@", lead)

        assert lead.email is None
