class SAAOrchestratorError(Exception):
    """Base exception class for SAA Orchestrator"""


class AssistantError(SAAOrchestratorError):
    """Raised when there's an error with an AI assistant"""


class WorkflowError(SAAOrchestratorError):
    """Raised when there's an error in the workflow execution"""


class ConfigurationError(SAAOrchestratorError):
    """Raised when there's an error in the configuration"""


class PluginError(SAAOrchestratorError):
    """Raised when there's an error with a plugin"""
