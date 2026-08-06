class JiraCardGeneratorError(Exception):
    """Base exception for deterministic business-rule failures."""


class CsvMappingError(JiraCardGeneratorError):
    """Raised when required Jira CSV columns cannot be mapped."""


class CsvValidationError(JiraCardGeneratorError):
    """Raised when Jira CSV content violates generation rules."""

