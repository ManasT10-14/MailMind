# llm/providers/gemini.py
from google.api_core.exceptions import ResourceExhausted
from src.llm.errors import UnifiedRateLimitError
from src.llm.providers.base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):

    def call(self, llm, messages, schema=None):
        try:
            if schema is not None:
                llm = llm.with_structured_output(schema)
            return llm.invoke(messages)

        except ResourceExhausted as e:
            raise UnifiedRateLimitError() from e
