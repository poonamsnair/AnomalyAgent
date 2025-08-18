from typing import Dict


class AgentError(Exception):
    """Base class for other agent-related exceptions"""

    def __init__(self, message, logger):
        super().__init__(message)
        self.message = message
        logger.log_error(message)

    def dict(self) -> dict[str, str]:
        return {"type": self.__class__.__name__, "message": str(self.message)}


class AgentParsingError(AgentError):
    """Exception raised for errors in parsing in the agent"""

    pass


class AgentExecutionError(AgentError):
    """Exception raised for errors in execution in the agent"""

    pass


class AgentMaxStepsError(AgentError):
    """Exception raised for errors in execution in the agent"""

    pass


class AgentToolCallError(AgentExecutionError):
    """Exception raised for errors when incorrect arguments are passed to the tool"""

    pass


class AgentToolExecutionError(AgentExecutionError):
    """Exception raised for errors when executing a tool"""

    pass


class AgentGenerationError(AgentError):
    """Exception raised for errors in generation in the agent"""

    pass