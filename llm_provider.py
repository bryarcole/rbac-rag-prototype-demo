"""
Multi-provider LLM abstraction layer.
Supports: AWS Bedrock, Google Gemini, OpenAI
"""
import os
import json
import logging
import re
import time
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Convert text to embedding vector."""
        pass

    @abstractmethod
    def generate_answer(
        self,
        question: str,
        context: str,
        system_prompt: str,
    ) -> Tuple[str, int, int, float]:
        """Generate answer with grounding. Returns (answer, input_tokens, output_tokens, cost_usd)."""
        pass


class BedrockProvider(LLMProvider):
    """AWS Bedrock provider."""

    def __init__(self):
        import boto3

        self.region = os.getenv("AWS_REGION", "us-east-2")
        self.chat_model_id = os.getenv("BEDROCK_CHAT_MODEL_ID", "us.amazon.nova-2-lite-v1:0")
        self.embed_model_id = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
        self.input_cost_per_1m = float(os.getenv("INPUT_COST_PER_1M", "0.30"))
        self.output_cost_per_1m = float(os.getenv("OUTPUT_COST_PER_1M", "2.50"))

        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=self.region)
            logger.info(f"✅ Bedrock provider initialized (region: {self.region})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Bedrock: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Bedrock Titan."""
        payload = json.dumps({"inputText": text, "dimensions": 1024, "normalize": True})
        response = self.bedrock.invoke_model(
            modelId=self.embed_model_id,
            body=payload,
            contentType="application/json",
            accept="application/json",
        )
        body = json.loads(response["body"].read())
        return body["embedding"]

    def generate_answer(
        self, question: str, context: str, system_prompt: str
    ) -> Tuple[str, int, int, float]:
        """Generate answer using Bedrock Converse API."""
        user_message = f"Context:\n{context}\n\nQuestion: {question}"

        response = self.bedrock.converse(
            modelId=self.chat_model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"temperature": 0.0, "maxTokens": 400},
        )

        answer = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})
        input_tokens = int(usage.get("inputTokens", 0))
        output_tokens = int(usage.get("outputTokens", 0))
        cost_usd = round(
            (input_tokens / 1_000_000) * self.input_cost_per_1m
            + (output_tokens / 1_000_000) * self.output_cost_per_1m,
            6,
        )
        return answer, input_tokens, output_tokens, cost_usd


def _retry_on_rate_limit(call, attempts: int = 6):
    """Retry a Gemini call that hit a per-minute quota, sleeping for the delay the API suggests."""
    from google.api_core.exceptions import ResourceExhausted

    for attempt in range(attempts):
        try:
            return call()
        except ResourceExhausted as exc:
            if attempt == attempts - 1:
                raise
            match = re.search(r"retry in ([\d.]+)s", str(exc))
            delay = float(match.group(1)) + 1 if match else 30
            logger.warning("Gemini rate limit hit, retrying in %.0fs", delay)
            time.sleep(delay)


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self):
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.embed_model = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")
        self.chat_model_id = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
        self.input_cost_per_1m = float(os.getenv("GEMINI_INPUT_COST_PER_1M", "0.025"))
        self.output_cost_per_1m = float(os.getenv("GEMINI_OUTPUT_COST_PER_1M", "0.10"))

        logger.info("✅ Gemini provider initialized")

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Gemini."""
        import google.generativeai as genai

        result = _retry_on_rate_limit(lambda: genai.embed_content(model=self.embed_model, content=text))
        return result["embedding"]

    def generate_answer(
        self, question: str, context: str, system_prompt: str
    ) -> Tuple[str, int, int, float]:
        """Generate answer using Gemini."""
        import google.generativeai as genai

        model = genai.GenerativeModel(
            self.chat_model_id,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=400,
            ),
        )

        user_message = f"Context:\n{context}\n\nQuestion: {question}"
        response = _retry_on_rate_limit(lambda: model.generate_content(user_message))
        answer = response.text

        # Gemini doesn't expose token counts in free tier, estimate based on text length
        input_tokens = len(context.split()) + len(question.split())
        output_tokens = len(answer.split())
        cost_usd = round(
            (input_tokens / 1_000_000) * self.input_cost_per_1m
            + (output_tokens / 1_000_000) * self.output_cost_per_1m,
            6,
        )
        return answer, input_tokens, output_tokens, cost_usd


class OpenAIProvider(LLMProvider):
    """OpenAI provider."""

    def __init__(self):
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        self.embed_model = "text-embedding-3-small"
        self.chat_model = "gpt-4o-mini"
        self.input_cost_per_1m = float(os.getenv("OPENAI_INPUT_COST_PER_1M", "0.02"))
        self.output_cost_per_1m = float(os.getenv("OPENAI_OUTPUT_COST_PER_1M", "0.15"))

        logger.info("✅ OpenAI provider initialized")

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI."""
        response = self.client.embeddings.create(input=text, model=self.embed_model)
        return response.data[0].embedding

    def generate_answer(
        self, question: str, context: str, system_prompt: str
    ) -> Tuple[str, int, int, float]:
        """Generate answer using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.chat_model,
            temperature=0.0,
            max_tokens=400,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                }
            ],
        )

        answer = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost_usd = round(
            (input_tokens / 1_000_000) * self.input_cost_per_1m
            + (output_tokens / 1_000_000) * self.output_cost_per_1m,
            6,
        )
        return answer, input_tokens, output_tokens, cost_usd


def get_provider() -> LLMProvider:
    """Factory function to get the configured LLM provider."""
    provider_name = os.getenv("LLM_PROVIDER", "bedrock").lower()

    if provider_name == "bedrock":
        return BedrockProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
