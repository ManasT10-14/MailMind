from src.llm.retry_llm import call_llm_with_retry
def call_llm_cached(
    *,
    cache,                      # SQLiteLLMCache instance
    llm,
    provider,                   # BaseLLMProvider
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    output_schema,              # Pydantic model (e.g. Cells)
    prompt_version: str,
    agent_name: str,
):

    schema_json = output_schema.model_json_schema()


    cache_key = cache.make_cache_key(
        model_name=model_name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=schema_json,
        prompt_version=prompt_version,
        agent_name=agent_name,
    )


    cached = cache.get(cache_key)
    if cached is not None:
        return output_schema.model_validate(cached)

    def _call():
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return provider.call(llm, messages, schema=output_schema)

    response = call_llm_with_retry(_call)

    cache.set(cache_key, response.model_dump())

    return response
