# llm/providers/base.py
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):

    @abstractmethod
    def call(
        self,
        llm,
        messages,
        schema=None,
    ):
        """Call the provider and return the result."""
        pass
