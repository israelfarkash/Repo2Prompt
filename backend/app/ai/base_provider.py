"""
Abstract base class for AI providers.

Defines the interface that all AI providers must implement for the
AI Project Reverse Engineer analysis pipeline.
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Abstract base class defining the contract for AI analysis providers.

    All AI providers (Gemini, OpenAI, Anthropic, etc.) must implement
    these methods to be compatible with the analysis pipeline.
    """

    @abstractmethod
    async def analyze_code(self, code: str, file_path: str, context: str) -> dict:
        """
        Analyze a single code file and extract structured information.

        Args:
            code: The raw source code content of the file.
            file_path: The relative path of the file within the project
                       (e.g., 'src/utils/helpers.py').
            context: Additional context about the project or surrounding files
                     to improve analysis accuracy.

        Returns:
            A dictionary containing:
                - purpose (str): A concise description of what the file does.
                - key_components (list[dict]): List of functions/classes with
                  keys 'name', 'type' ('function'|'class'|'method'), and
                  'description'.
                - design_patterns (list[str]): Design patterns identified in
                  the code (e.g., 'Singleton', 'Factory', 'Observer').
                - dependencies (list[str]): Import statements and external
                  dependencies used by the file.
                - connections (list[str]): Other files or modules this file
                  interacts with or references.
                - complexity_assessment (str): A brief assessment of the code's
                  complexity level ('low', 'medium', 'high') with reasoning.
        """
        ...

    @abstractmethod
    async def analyze_architecture(self, structure: dict, tech_stack: dict) -> dict:
        """
        Analyze the overall project architecture based on file structure and
        detected technology stack.

        Args:
            structure: A nested dictionary representing the project's file tree.
                       Keys are directory/file names, values are either nested
                       dicts (for directories) or file metadata dicts.
            tech_stack: A dictionary describing detected technologies, e.g.,
                        {'languages': [...], 'frameworks': [...],
                         'databases': [...], 'tools': [...]}.

        Returns:
            A dictionary containing:
                - architecture_pattern (str): The identified architectural
                  pattern (e.g., 'MVC', 'Microservices', 'Monolith',
                  'Layered', 'Event-Driven').
                - layers (list[dict]): List of architectural layers, each with
                  'name', 'description', and 'directories' keys.
                - data_flow (str): A description of how data flows through
                  the system.
                - entry_points (list[str]): Main entry points of the
                  application (e.g., 'main.py', 'index.js').
                - key_directories_purposes (dict): Mapping of important
                  directory names to their purposes.
        """
        ...

    @abstractmethod
    async def analyze_section(
        self, section_name: str, files_content: dict, context: str
    ) -> dict:
        """
        Analyze a logical section of the project (e.g., 'backend', 'frontend',
        'database', 'infrastructure').

        Args:
            section_name: The name of the section being analyzed
                          (e.g., 'backend', 'frontend', 'database').
            files_content: A dictionary mapping file paths to their source code
                           content for all files in this section.
            context: Additional context about the overall project to provide
                     cross-section awareness.

        Returns:
            A dictionary containing:
                - section_overview (str): A high-level summary of this section's
                  role and responsibilities.
                - key_components (list[dict]): Important components with 'name',
                  'file_path', 'type', and 'description' keys.
                - patterns_used (list[str]): Design and architectural patterns
                  found in this section.
                - dependencies (dict): Internal and external dependencies with
                  keys 'internal' (list) and 'external' (list).
                - functionality_map (dict): Mapping of features/functionalities
                  to the files that implement them.
        """
        ...

    @abstractmethod
    async def generate_synthesis(
        self, analyses: list[dict], project_info: dict
    ) -> str:
        """
        Generate a comprehensive mega-prompt document by synthesizing all
        individual analyses into a cohesive project specification.

        Args:
            analyses: A list of all analysis results from previous stages,
                      including code analyses, architecture analysis, and
                      section analyses.
            project_info: General project information including name,
                          description, repository URL, detected languages,
                          frameworks, and file count.

        Returns:
            A comprehensive markdown-formatted mega-prompt string containing
            all 11 sections:
                1. Project Overview
                2. Technologies & Stack
                3. Architecture & Design Patterns
                4. Folder Structure & File Organization
                5. Features & Functionality
                6. Database Design & Data Models
                7. API Documentation & Endpoints
                8. Authentication & Authorization
                9. UI/UX Description & Component Hierarchy
                10. Development Setup Instructions
                11. Final Build & Deployment Instructions
        """
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Return the name/identifier of the AI model being used.

        Returns:
            A string identifying the model (e.g., 'gemini-2.5-flash',
            'gpt-4o', 'claude-sonnet-4-20250514').
        """
        ...
