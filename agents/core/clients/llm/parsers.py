import json
from datetime import datetime
from core.models import LLMResponse, Message, ToolResult, Usage, TextContent, ImageContent, ToolCall
from core.clients.llm.utils import parse_timestamp, calculate_cost_in_usd
from uuid import uuid4

def parse_openai_response(raw, provider: str) -> LLMResponse:
    choice = raw.choices[0]
    msg = choice.message

    tool_calls = []
    if msg.tool_calls:
        for tc in msg.tool_calls:
            tool_calls.append(ToolCall(
                id=tc.id,
                name=tc.function.name,
                arguments=json.loads(tc.function.arguments)
            ))

    # --- Calculate cost
    cost_in_usd = calculate_cost_in_usd(
        provider=provider,
        model_name=raw.model,
        input_tokens=raw.usage.prompt_tokens,
        output_tokens=raw.usage.completion_tokens
    )

    return LLMResponse(
        id=raw.id,
        provider=provider,
        model=raw.model,
        created_at=parse_timestamp(raw.created),
        message=Message(
            role=msg.role,
            content=msg.content,
            tool_calls=tool_calls if tool_calls else None,
            tool_result=None
        ),
        finish_reason=choice.finish_reason,
        usage=Usage(
            prompt_tokens=raw.usage.prompt_tokens,
            completion_tokens=raw.usage.completion_tokens,
            total_tokens=raw.usage.total_tokens,
            cost=cost_in_usd
        )
    )


def parse_anthropic_response(raw) -> LLMResponse:
    text = None
    tool_calls = []

    for item in raw.content:
        if item.type == "text":
            text=item.text
        elif item.type == "tool_use":
            tool_calls.append(ToolCall(
                id=item.id,
                name=item.name,
                arguments=item.input
            ))

    # Cost calculation
    prompt_tokens = raw.usage.input_tokens or 0
    completion_tokens = raw.usage.output_tokens or 0
    cost_in_usd = calculate_cost_in_usd(
        provider="anthropic",
        model_name=raw.model,
        input_tokens=prompt_tokens,
        output_tokens=completion_tokens
    )

    return LLMResponse(
        id=raw.id,
        provider="anthropic",
        model=raw.model,
        created_at=datetime.utcnow(),
        message=Message(
            role=raw.role,
            content=text,
            tool_calls=tool_calls or None,
            tool_result=None
        ),
        finish_reason=raw.stop_reason,
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=cost_in_usd
        )
    )


def parse_ollama_response(raw) -> LLMResponse:
    msg = raw.message

    tool_calls = []
    if getattr(msg, "tool_calls", None):
        for call in msg.tool_calls:
            tool_calls.append(ToolCall(
                id=f"{uuid4()}",  # Ollama does not provide call ID
                name=call.function.name,
                arguments=call.function.arguments
            ))

    # Calculate cost in USD
    prompt_tokens = raw.prompt_eval_count or 0
    completion_tokens = raw.eval_count or 0
    cost_in_usd = calculate_cost_in_usd(
        provider="ollama",
        model_name=raw.model,
        input_tokens=prompt_tokens,
        output_tokens=completion_tokens
    )

    return LLMResponse(
        id="ollama-" + raw.created_at,  # Ollama doesn't have IDs, use timestamp
        provider="ollama",
        model=raw.model,
        created_at=parse_timestamp(raw.created_at),
        message=Message(
            role=msg.role,
            content=msg.content,
            tool_calls=tool_calls or None,
            tool_result=None
        ),
        finish_reason=raw.done_reason,
        usage=Usage(
            prompt_tokens=raw.prompt_eval_count,
            completion_tokens=raw.eval_count,
            total_tokens=(raw.prompt_eval_count or 0) + (raw.eval_count or 0),
            cost=cost_in_usd
        )
    )

