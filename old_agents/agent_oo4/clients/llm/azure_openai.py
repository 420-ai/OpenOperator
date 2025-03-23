import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

class LLMResponseOpenAI:
    def __init__(self, response):
        self._response = response

    # --------------------------------
    # Choice[0]
    # --------------------------------

    @property
    def raw_message(self):
        return self._response.choices[0].message

    @property
    def message(self):
        """Return the message content."""
        return self._response.choices[0].message.content if self._response.choices else None

    @property
    def message_json(self):
        """Return message as a JSON string."""
        return json.dumps({"message": self.message}, indent=2, ensure_ascii=False)

    @property
    def finish_reason(self):
        return self._response.choices[0].finish_reason if self._response.choices else None

    @property
    def tool_calls(self):
        return self._response.choices[0].message.tool_calls if self._response.choices else None

    @property
    def tool_calls_json(self):
        """Return tool calls as a list of dicts (serializable)."""
        if not self.tool_calls:
            return None
        try:
            return [tc.model_dump() for tc in self.tool_calls]
        except AttributeError:
            # Fallback for older SDK versions
            return [tc.to_dict() if hasattr(tc, 'to_dict') else str(tc) for tc in self.tool_calls]
 
    # --------------------------------
    # Choices
    # --------------------------------

    @property
    def messages(self):
        return [choice.message.content for choice in self._response.choices]

    @property
    def messages_json(self):
        return [json.dumps({"message": choice.message.content}, indent=2, ensure_ascii=False) for choice in self._response.choices]

    @property
    def finish_reasons(self):
        return [choice.finish_reason for choice in self._response.choices]

    # --------------------------------
    # Usage
    # --------------------------------

    @property
    def usage(self):
        u = self._response.usage
        return {"prompt": u.prompt_tokens, "completion": u.completion_tokens} if u else None

    # --------------------------------
    # Original Response
    # --------------------------------

    @property
    def raw_response(self):
        return self._response
    
    @property
    def raw_message(self):
        return self._response.choices[0].message
    


    def to_dict(self):
        return {
            "message": self.message,
            "finish_reason": self.finish_reason,
            "usage": self.usage
        }

    def to_json(self, indent: int = 2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_full_json(self):
        return self._response.to_json()

    def __repr__(self):
        return f"<LLMResponseOpenAI choices={len(self.messages)}, usage={self.usage}>"


class OOAzureOpenAIClient:
    def __init__(self, deployment: str, model: str):
        """
        Initializes the custom LLM client.
        
        :param deployment: The deployment name (e.g., "gpt-4o-deployment").
        """
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_BASEURL"),
            azure_ad_token=os.getenv("AZURE_API_KEY"),
            azure_deployment=deployment,
        )
        self.model = model 

    def call(self, messages, tools=None, tool_choice="auto", n=1, temperature=0.1):
        """
        Creates a chat completion request.

        :param messages: List of messages (system, user, etc.).
        :param tools: Custom tools for the LLM (optional).
        :param tool_choice: Tool selection mode (default: "auto").
        :param n: Number of completions to generate (default: 1).
        :param temperature: Sampling temperature (default: 0.1).
        :return: Chat completion result.
        """

        params = {
            "model": self.model,
            "messages": messages,
            "n": n,
            "temperature": temperature
        }

        if tools is not None:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return LLMResponseOpenAI(response)


llm_o3_mini = OOAzureOpenAIClient(
    model="o3-mini",
    deployment="o3-mini-deployment"
)

llm_gpt4o = OOAzureOpenAIClient(
    model="gpt-4o",
    deployment="gpt-4o-deployment"
)

llm_gpt4o_mini = OOAzureOpenAIClient(
    model="gpt-4o-mini",
    deployment="gpt-4o-mini-deployment"
)


