import anthropic
from ..config import settings
from ..schemas.parse import ParsedJob

_EXTRACT_TOOL = {
    "name": "extract_job_fields",
    "description": "Extract structured fields from a raw job posting.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Job title exactly as written",
            },
            "company": {
                "type": "string",
                "description": "Company or organization name",
            },
            "location": {
                "type": "string",
                "description": "Job location (city/state, 'Remote', 'Hybrid', etc.)",
            },
            "salary_min": {
                "type": "integer",
                "description": "Minimum annual salary in USD as a plain integer (e.g. 90000). Omit if not stated.",
            },
            "salary_max": {
                "type": "integer",
                "description": "Maximum annual salary in USD as a plain integer (e.g. 120000). Omit if not stated.",
            },
            "url": {
                "type": "string",
                "description": "Job posting URL if present in the text",
            },
            "description": {
                "type": "string",
                "description": "A concise 2-3 sentence summary of the role, team, and key responsibilities",
            },
            "skills_mentioned": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Technical skills, tools, languages, and technologies mentioned (e.g. 'Python', 'SQL', 'AWS')",
            },
        },
        "required": ["title"],
    },
}


async def parse_job_description(text: str) -> ParsedJob:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=[_EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": "extract_job_fields"},
        messages=[
            {
                "role": "user",
                "content": f"Extract structured fields from this job posting:\n\n{text[:8000]}",
            }
        ],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_job_fields":
            return ParsedJob(**block.input)
    return ParsedJob(title="Unknown")