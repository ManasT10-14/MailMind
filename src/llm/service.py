from src.llm.retry_llm import call_llm_with_retry

def call_llm_cached(
    *,
    cache,
    llm,
    provider,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    output_schema,
    prompt_version: str,
    agent_name: str,
    cache_enabled: bool = True,
):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    def _call():
        return provider.call(llm, messages, schema=output_schema)

    if not cache_enabled:
        return call_llm_with_retry(_call)


    cache_key = cache.make_cache_key(
        model_name=model_name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=output_schema.model_json_schema(),
        prompt_version=prompt_version,
        agent_name=agent_name,
    )

    cached = cache.get(cache_key)
    if cached is not None:
        return output_schema.model_validate(cached)

    response = call_llm_with_retry(_call)

    cache.set(cache_key, response.model_dump())

    return response
