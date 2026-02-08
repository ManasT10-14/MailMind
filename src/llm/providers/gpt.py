from openai import RateLimitError
from src.llm.errors import UnifiedRateLimitError
from src.llm.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):

    def call(self, llm, messages, schema=None):
        try:
            if schema is not None:
                llm = llm.with_structured_output(schema)

            return llm.invoke(messages)

        except RateLimitError as e:
            raise UnifiedRateLimitError() from e
