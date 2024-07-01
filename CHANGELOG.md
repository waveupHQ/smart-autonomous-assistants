# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2024-06-30

### Added

- Implement dynamic assistant creation supporting Anthropic, OpenAI, and Google LLMs
- Add configuration settings for VertexAI project and location
- Update requirements and setup files with new dependencies
- Refactor assistants module to use fallback mechanisms and retry logic
- Enhance orchestrator with improved logging and docstrings
- Add CI workflow for testing, linting, and formatting
- Update project structure and .gitignore rules

## [0.1.0] - 2024-06-29

### Added

- Initial release of Smart Autonomous Assistants (SAAs)
- Core functionality including Orchestrator, MainAssistant, SubAssistant, and RefinerAssistant
- File operations for creating, reading, and listing files
- Command-line interface for running workflows
- Configuration management using pydantic and python-dotenv
- Basic error handling and logging
