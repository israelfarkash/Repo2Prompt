"""
Gemini AI provider implementation using the google-genai SDK.

Provides all analysis capabilities for the AI Project Reverse Engineer
pipeline, including code analysis, architecture analysis, section analysis,
and comprehensive mega-prompt synthesis.
"""

import asyncio
import json
import logging
import random
import re

from google import genai

from .base_provider import AIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    AI provider implementation powered by Google's Gemini models.

    Uses the google-genai SDK for async content generation with built-in
    retry logic and robust JSON response parsing.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        """
        Initialize the Gemini provider.

        Args:
            api_key: Google AI API key for authentication.
            model: The Gemini model identifier to use. Defaults to
                   'gemini-2.5-flash' for optimal speed/quality balance.
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        logger.info("GeminiProvider initialized with model: %s", self.model)

    def get_model_name(self) -> str:
        """Return the Gemini model identifier being used."""
        return self.model

    # ------------------------------------------------------------------
    # Core analysis methods
    # ------------------------------------------------------------------

    async def analyze_code(self, code: str, file_path: str, context: str) -> dict:
        """Analyze a single code file and return structured metadata."""
        logger.info("Analyzing code file: %s", file_path)

        prompt = f"""You are an expert software engineer performing a deep analysis of a source code file.

**File path:** `{file_path}`

**Project context:**
{context}

**Source code:**
```
{code}
```

Analyze this file thoroughly and return a JSON object with EXACTLY these keys:

{{
  "purpose": "A concise description of what this file does and its role in the project",
  "key_components": [
    {{
      "name": "component_name",
      "type": "function|class|method|constant|middleware|route|hook",
      "description": "What this component does and why it exists"
    }}
  ],
  "design_patterns": ["List of design patterns used, e.g. Singleton, Factory, Observer, Repository, MVC, Decorator"],
  "dependencies": ["List of all import statements and external libraries used"],
  "connections": ["List of other files/modules this file interacts with, references, or imports from"],
  "complexity_assessment": "low|medium|high — with a brief explanation of why"
}}

Rules:
- Be thorough — list ALL functions, classes, and significant constants.
- For connections, infer related files even if not directly imported (e.g., if a model file references a schema, note the schema file).
- For design patterns, only list patterns that are clearly present, not speculative ones.
- Return ONLY valid JSON, no markdown formatting, no extra text."""

        try:
            text = await self._call_with_retry(prompt)
            result = self._parse_json_response(text)
            logger.info("Successfully analyzed code file: %s", file_path)
            return result
        except Exception as e:
            logger.error("Failed to analyze code file %s: %s", file_path, str(e))
            return {
                "purpose": f"Analysis failed: {str(e)}",
                "key_components": [],
                "design_patterns": [],
                "dependencies": [],
                "connections": [],
                "complexity_assessment": "unknown",
            }

    async def analyze_architecture(
        self, structure: dict, tech_stack: dict
    ) -> dict:
        """Analyze overall project architecture from file tree and tech stack."""
        logger.info("Analyzing project architecture")

        structure_str = json.dumps(structure, indent=2, ensure_ascii=False)
        tech_stack_str = json.dumps(tech_stack, indent=2, ensure_ascii=False)

        prompt = f"""You are a senior software architect analyzing a project's overall architecture.

**Project file tree structure:**
```json
{structure_str}
```

**Detected technology stack:**
```json
{tech_stack_str}
```

Based on the file tree and technology stack, determine the project's architecture. Return a JSON object with EXACTLY these keys:

{{
  "architecture_pattern": "The primary architectural pattern (e.g., MVC, MVVM, Microservices, Monolith, Layered, Hexagonal, Event-Driven, Serverless, JAMstack, Clean Architecture)",
  "layers": [
    {{
      "name": "Layer name (e.g., Presentation, Business Logic, Data Access, Infrastructure)",
      "description": "What this layer is responsible for",
      "directories": ["List of directories that belong to this layer"]
    }}
  ],
  "data_flow": "A clear description of how data flows through the system, from user input to storage and back. Mention specific components involved.",
  "entry_points": ["List of main entry point files (e.g., main.py, index.js, App.tsx, server.ts)"],
  "key_directories_purposes": {{
    "directory_name": "Purpose and responsibility of this directory"
  }}
}}

Rules:
- Identify ALL layers present in the architecture, not just the main ones.
- For data_flow, trace a typical request from start to finish.
- List every significant directory in key_directories_purposes.
- Be specific about which directories map to which layers.
- Return ONLY valid JSON, no markdown formatting, no extra text."""

        try:
            text = await self._call_with_retry(prompt)
            result = self._parse_json_response(text)
            logger.info("Successfully analyzed project architecture")
            return result
        except Exception as e:
            logger.error("Failed to analyze architecture: %s", str(e))
            return {
                "architecture_pattern": f"Analysis failed: {str(e)}",
                "layers": [],
                "data_flow": "Unknown",
                "entry_points": [],
                "key_directories_purposes": {},
            }

    async def analyze_section(
        self, section_name: str, files_content: dict, context: str
    ) -> dict:
        """Analyze a logical section of the project in depth."""
        logger.info("Analyzing section: %s (%d files)", section_name, len(files_content))

        # Build a condensed view of file contents — truncate very large files
        # to stay within context window limits.
        files_summary_parts: list[str] = []
        for path, content in files_content.items():
            truncated = content[:8000] if len(content) > 8000 else content
            suffix = "\n... [truncated]" if len(content) > 8000 else ""
            files_summary_parts.append(
                f"### File: `{path}`\n```\n{truncated}{suffix}\n```"
            )
        files_block = "\n\n".join(files_summary_parts)

        prompt = f"""You are a senior software engineer performing an in-depth analysis of the **{section_name}** section of a software project.

**Overall project context:**
{context}

**Files in the "{section_name}" section:**

{files_block}

Analyze this section thoroughly and return a JSON object with EXACTLY these keys:

{{
  "section_overview": "A comprehensive summary of what this section does, its responsibilities, and how it fits into the overall project",
  "key_components": [
    {{
      "name": "Component name",
      "file_path": "path/to/file",
      "type": "service|controller|model|utility|middleware|component|hook|config|migration|test",
      "description": "Detailed description of what this component does"
    }}
  ],
  "patterns_used": ["List of design and architectural patterns found (e.g., Repository Pattern, Dependency Injection, HOC, Redux Pattern, Middleware Chain)"],
  "dependencies": {{
    "internal": ["List of internal project modules/packages this section depends on"],
    "external": ["List of external libraries/packages this section depends on"]
  }},
  "functionality_map": {{
    "Feature or functionality name": ["file1.py", "file2.py — files that implement this feature"]
  }}
}}

Rules:
- Be exhaustive in listing key_components — every significant file should be represented.
- Group related files under clear functionality names in the functionality_map.
- Distinguish between internal (same project) and external (npm/pip packages) dependencies.
- For patterns_used, only list patterns that are clearly present.
- Return ONLY valid JSON, no markdown formatting, no extra text."""

        try:
            text = await self._call_with_retry(prompt)
            result = self._parse_json_response(text)
            logger.info("Successfully analyzed section: %s", section_name)
            return result
        except Exception as e:
            logger.error("Failed to analyze section %s: %s", section_name, str(e))
            return {
                "section_overview": f"Analysis failed: {str(e)}",
                "key_components": [],
                "patterns_used": [],
                "dependencies": {"internal": [], "external": []},
                "functionality_map": {},
            }

    async def generate_synthesis(
        self, analyses: list[dict], project_info: dict
    ) -> str:
        """Synthesize all analyses into a comprehensive mega-prompt document."""
        logger.info(
            "Generating synthesis from %d analyses for project: %s",
            len(analyses),
            project_info.get("name", "Unknown"),
        )

        analyses_str = json.dumps(analyses, indent=2, ensure_ascii=False)
        project_info_str = json.dumps(project_info, indent=2, ensure_ascii=False)

        prompt = f"""You are an elite software architect and technical writer. Your task is to synthesize all of the following analysis data into a single, comprehensive **Mega-Prompt** document.

This Mega-Prompt must be so detailed and precise that a skilled developer (or an AI coding assistant) could use it to **faithfully recreate the entire project from scratch**.

**Project information:**
```json
{project_info_str}
```

**All analysis results:**
```json
{analyses_str}
```

Generate a comprehensive Markdown document with EXACTLY these 11 sections. Each section must be thorough, specific, and actionable:

---

# 1. Project Overview
- Project name, purpose, and problem it solves
- Target users and use cases
- Core value proposition
- High-level description of how the system works end-to-end

# 2. Technologies & Stack
- Complete list of ALL languages, frameworks, libraries, and tools
- **CRITICAL:** You MUST specify exact versions (e.g., Target SDK 34, Min SDK 26, Node 20.x, Kotlin 2.0). If versions are missing from the data, you MUST infer and assign the most appropriate modern stable version to prevent compile errors.
- Why each technology was chosen (infer from usage patterns)
- Development vs. production dependencies

# 3. Architecture & Design Patterns
- Primary architectural pattern and justification
- All design patterns used throughout the codebase
- System component diagram (described textually)
- How components communicate with each other
- Separation of concerns strategy

# 4. Folder Structure & File Organization
- Complete directory tree with descriptions
- Naming conventions used
- Where to find specific types of code
- Configuration file locations and purposes

# 5. Features & Functionality (Behind the Scenes)
- Complete list of features organized by module/section
- **CRITICAL:** Do not just explain *what* the feature does, explain *HOW* it works technically at a low level (e.g., how the MediaSession manages state, how WebSockets sync data, how external JS scripts are executed natively).
- User-facing vs. system-level features
- Feature dependencies and relationships

# 6. Database Design & Data Models
- All data models/schemas with EXACT field definitions and types. Do not leave this ambiguous.
- Relationships between models (one-to-many, many-to-many, etc.)
- Indexes and constraints
- Migration strategy
- If no database: state management approach

# 7. API Documentation & Endpoints
- Every API endpoint with method, path, request/response formats
- Authentication requirements per endpoint
- Error handling patterns
- If no API: inter-component communication patterns

# 8. Authentication & Authorization
- Authentication strategy (JWT, OAuth, sessions, etc.)
- **CRITICAL:** Detail the exact scopes needed, token rotation mechanisms, and backend API contract for authentication.
- Authorization model (RBAC, ABAC, etc.)
- Security measures implemented
- If no auth: note this explicitly

# 9. UI/UX Description & Component Hierarchy
- Page/screen descriptions
- Component hierarchy and relationships
- Styling approach and design system
- Responsive design strategy
- If no UI: CLI or interface description

# 10. Development Setup Instructions
- Prerequisites and system requirements
- Step-by-step setup instructions
- Environment variables needed (with descriptions, not values)
- How to run the development server
- How to run tests

# 11. Final Build & Deployment Instructions
- Build process and commands
- Deployment target and strategy
- Environment configuration for production
- CI/CD pipeline description (if present)
- Post-deployment verification steps

# 12. Execution Plan (Iterative Prompting)
- **CRITICAL:** Provide a step-by-step execution plan for the AI that will read this prompt.
- Instruct the AI NOT to write all the code at once to avoid context limits.
- Example: "Step 1: Setup project structure and configuration files. Ask for approval. Step 2: Implement Database entities and schemas. Ask for approval. Step 3: Implement core services..."

---

IMPORTANT RULES:
- Be extremely specific — use actual file names, function names, and component names from the analysis data.
- Do NOT use "[INSUFFICIENT DATA]" if you can safely infer or mock a standard implementation. For example, if a "Listen Together" or social feature exists but server details are missing, explicitly instruct the target AI to build a mock server (e.g., Node.js or Ktor) to support it.
- Write in a clear, imperative style suitable for use as a development specification.
- The output should be valid Markdown.
- This document should be self-contained — a developer should not need any other reference."""

        try:
            text = await self._call_with_retry(prompt)
            logger.info("Successfully generated synthesis document")
            return text
        except Exception as e:
            logger.error("Failed to generate synthesis: %s", str(e))
            return (
                f"# Synthesis Generation Failed\n\n"
                f"An error occurred while generating the mega-prompt synthesis.\n\n"
                f"**Error:** {str(e)}\n\n"
                f"**Project:** {project_info.get('name', 'Unknown')}\n\n"
                f"**Analyses collected:** {len(analyses)}\n\n"
                f"Please retry the synthesis step or check the AI provider configuration."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _call_with_retry(
        self, prompt: str, max_retries: int = 5
    ) -> str:
        """
        Call the Gemini API with exponential backoff retry logic.

        Args:
            prompt: The prompt text to send to the model.
            max_retries: Maximum number of attempts before raising.

        Returns:
            The text response from the model.

        Raises:
            Exception: Re-raises the last exception after all retries
                       are exhausted.
        """
        for attempt in range(max_retries):
            try:
                logger.debug(
                    "API call attempt %d/%d (model=%s, prompt_length=%d)",
                    attempt + 1,
                    max_retries,
                    self.model,
                    len(prompt),
                )
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                if response.text is None:
                    raise ValueError(
                        "Gemini returned an empty response (response.text is None). "
                        "The prompt may have been blocked by safety filters."
                    )
                logger.debug(
                    "API call succeeded on attempt %d, response_length=%d",
                    attempt + 1,
                    len(response.text),
                )
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        "All %d API call attempts failed. Last error: %s",
                        max_retries,
                        str(e),
                    )
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    "API call attempt %d failed (%s: %s). Retrying in %.1fs...",
                    attempt + 1,
                    type(e).__name__,
                    str(e),
                    wait,
                )
                await asyncio.sleep(wait)

        # This line should never be reached, but satisfies type checkers.
        raise RuntimeError("Unexpected exit from retry loop")  # pragma: no cover

    def _parse_json_response(self, text: str) -> dict:
        """
        Parse a JSON object from the model's text response.

        Handles common cases where the model wraps JSON in markdown code
        fences or includes extra text around the JSON block.

        Args:
            text: The raw text response from the model.

        Returns:
            A parsed dictionary. If all parsing strategies fail, returns
            ``{"raw_response": text}`` as a fallback so that downstream
            code always receives a dict.
        """
        cleaned = text.strip()

        # Strategy 1: Direct parse — the response is pure JSON.
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from ```json ... ``` fenced code block.
        json_fence_match = re.search(
            r"```json\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL
        )
        if json_fence_match:
            try:
                return json.loads(json_fence_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Strategy 3: Extract from generic ``` ... ``` fenced code block.
        generic_fence_match = re.search(
            r"```\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL
        )
        if generic_fence_match:
            try:
                return json.loads(generic_fence_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Strategy 4: Find the first { ... } block (greedy) in the text.
        brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: return raw text wrapped in a dict.
        logger.warning(
            "Could not parse JSON from model response (length=%d). "
            "Returning raw_response fallback.",
            len(text),
        )
        return {"raw_response": text}
