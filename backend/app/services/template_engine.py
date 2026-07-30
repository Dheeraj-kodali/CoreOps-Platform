import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SUPPORTED_PLACEHOLDERS: List[str] = [
    "{name}",
    "{phone}",
    "{village}",
    "{persons}",
    "{purpose}",
    "{date}",
    "{time}",
    "{duration}",
    "{visitor_id}",
    "{temple}",
    "{volunteer}",
]

SAMPLE_CONTEXT: Dict[str, str] = {
    "name": "Ramesh Kumar",
    "phone": "+91 98765 43210",
    "village": "Chittoor",
    "persons": "3",
    "purpose": "General Darshan",
    "date": "2026-07-28",
    "time": "10:15 AM",
    "duration": "1 hr 25 min",
    "visitor_id": "VST-20260728-001",
    "temple": "Sri Kalki Seva Alayam",
    "volunteer": "Venkat",
}


class TemplateEngine:
    """
    Stateless template rendering engine.
    Replaces {placeholder} tokens in message templates with actual visitor/context values.
    """

    @staticmethod
    def render(template_text: str, context: Dict[str, str]) -> str:
        """
        Replace all supported placeholders in the template with values from the context dict.
        Unknown placeholders are left as-is.
        """
        rendered = template_text
        for key, value in context.items():
            placeholder = "{" + key + "}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered

    @staticmethod
    def get_supported_placeholders() -> List[str]:
        """Return the list of all supported placeholder tokens."""
        return list(SUPPORTED_PLACEHOLDERS)

    @staticmethod
    def preview(template_text: str, custom_context: Optional[Dict[str, str]] = None) -> str:
        """Render a template with sample data for preview purposes."""
        context = dict(SAMPLE_CONTEXT)
        if custom_context:
            context.update(custom_context)
        return TemplateEngine.render(template_text, context)

    @staticmethod
    def extract_placeholders(template_text: str) -> List[str]:
        """Extract all {placeholder} tokens found in the template text."""
        pattern = r"\{(\w+)\}"
        matches = re.findall(pattern, template_text)
        return ["{" + m + "}" for m in matches]
