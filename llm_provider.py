"""
Multi-provider LLM abstraction layer.
Supports: AWS Bedrock, Google Gemini, OpenAI

WHAT THIS FILE DOES
    The rest of the app never talks to Bedrock/Gemini/OpenAI directly. It asks `get_provider()` for
    an object with exactly two abilities:
        1. get_embedding(text)  -> list of floats   (turns text into a vector for similarity search)
        2. generate_answer(...) -> (answer, input_tokens, output_tokens, cost_usd)
    Swapping vendors is then a one-line config change (LLM_PROVIDER=bedrock|gemini|openai).

HOW TO READ THE "AWS EXAM" CALLOUTS (grep -rn "AWS EXAM" . to list them all)
    Tags:  [CLF-C02] = AWS Certified Cloud Practitioner
           [DVA-C02] = AWS Certified Developer - Associate
    Each callout is written as: the kind of question you might see, the answer, and WHY it is the
    answer. They are study aids written from general AWS knowledge, NOT questions from a real exam,
    and exam guides change. Check the current exam guide at https://aws.amazon.com/certification/.
    Most of this repo is Bedrock + IAM + logging + containers. It does NOT exercise S3, Lambda,
    DynamoDB, SQS/SNS or CloudFormation, which are all heavily tested on DVA-C02, so study those
    separately.
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
    """
    Base class for LLM providers (the "strategy pattern": same interface, interchangeable engines).

    `@abstractmethod` means a subclass that forgets to implement the method cannot even be created,
    so a half-finished provider fails at startup instead of in the middle of a user's request.
    """

    @property
    def embed_model_name(self) -> str:
        """Embedding model id, used to tell whether cached document embeddings are still valid."""
        # Bedrock stores it as `embed_model_id`; Gemini/OpenAI store it as `embed_model`.
        return getattr(self, "embed_model_id", None) or getattr(self, "embed_model", "unknown")

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
    """
    AWS Bedrock provider.

    Amazon Bedrock = a fully MANAGED, SERVERLESS service that gives one API to many foundation
    models (Amazon Titan/Nova, Anthropic Claude, Meta Llama, ...). There are no servers, GPUs or
    model files for you to manage.
    """

    def __init__(self):
        import boto3

        # ---------------------------------------------------------------------------------
        # Configuration comes from environment variables, not hard-coded values.
        # ---------------------------------------------------------------------------------
        # +- AWS EXAM [DVA-C02] -------------------------------------------------------------
        # | Q: Where should an app keep config and secrets (API keys, DB passwords)?
        # | A: Config -> environment variables / SSM Parameter Store. Secrets -> AWS Secrets
        # |    Manager (or Parameter Store SecureString), encrypted with KMS. Never in source code.
        # | WHY: Secrets Manager adds automatic rotation and fine-grained IAM access + audit
        # |    trail. Parameter Store is cheaper (standard tier is free) but has no built-in
        # |    rotation. Lambda env vars are encrypted at rest, but anyone who can read the
        # |    function config can read them, so they are fine for config, weaker for secrets.
        # +-------------------------------------------------------------------------------------
        #
        # +- AWS EXAM [CLF-C02 / DVA-C02] -----------------------------------------------------
        # | Q: Why does the same model work in one Region but fail in another?
        # | A: Foundation-model availability, quotas and your account's access are per-REGION.
        # | WHY: A Region is an isolated set of data centers. Services/features roll out per
        # |    Region. In THIS project, with the same key, Titan embeddings worked in us-west-2
        # |    but failed in us-east-1/us-east-2 with an account-verification error.
        # |    (Also: data stays in the Region you choose, which matters for compliance.)
        # +-------------------------------------------------------------------------------------
        self.region = os.getenv("AWS_REGION", "us-east-2")

        # +- AWS EXAM [DVA-C02] ---------------------------------------------------------------
        # | Q: What does the "us." prefix in "us.amazon.nova-2-lite-v1:0" mean?
        # | A: It is a cross-Region INFERENCE PROFILE id, not a plain model id.
        # | WHY: An inference profile lets Bedrock route your request to any Region in a group
        # |    (here: US Regions) to absorb traffic spikes and raise throughput, instead of being
        # |    limited to one Region's capacity. Side effect to know: a request sent to us-west-2
        # |    can be served elsewhere in the group, so a problem in another Region can still
        # |    reach you (we saw exactly that kind of error in this project).
        # +-------------------------------------------------------------------------------------
        self.chat_model_id = os.getenv("BEDROCK_CHAT_MODEL_ID", "us.amazon.nova-2-lite-v1:0")
        self.embed_model_id = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

        # Prices per 1 million tokens, used only for the cost estimate shown in the UI.
        # +- AWS EXAM [CLF-C02] ---------------------------------------------------------------
        # | Q: How is on-demand Bedrock text generation billed?
        # | A: Pay-as-you-go, per input token and per output token (output usually costs more).
        # | WHY: No upfront cost or servers to pay for while idle. For steady, high, predictable
        # |    volume you can instead buy PROVISIONED THROUGHPUT (reserved model capacity billed
        # |    by time). That is the same on-demand vs reserved trade-off as EC2.
        # | NOTE: these numbers are hard-coded estimates and WILL drift. For real numbers use the
        # |    AWS Pricing pages / Cost Explorer, and set an AWS Budgets alert.
        # +-------------------------------------------------------------------------------------
        self.input_cost_per_1m = float(os.getenv("INPUT_COST_PER_1M", "0.30"))
        self.output_cost_per_1m = float(os.getenv("OUTPUT_COST_PER_1M", "2.50"))

        try:
            # +- AWS EXAM [DVA-C02] -----------------------------------------------------------
            # | Q: Which boto3 client do you use to CALL a model, "bedrock" or "bedrock-runtime"?
            # | A: "bedrock-runtime".
            # | WHY: AWS splits services into a CONTROL plane and a DATA plane.
            # |    "bedrock"          = control plane: list models, manage guardrails, provisioned
            # |                         throughput, model customization jobs.
            # |    "bedrock-runtime"  = data plane: InvokeModel / Converse (what we do here).
            # |    "bedrock-agent-runtime" = Knowledge Bases / Agents queries (Retrieve, etc.).
            # |
            # | Q: Where do the credentials come from? We pass none!
            # | A: boto3's DEFAULT CREDENTIAL PROVIDER CHAIN, checked in this rough order:
            # |    1) explicit params in code  2) env vars AWS_ACCESS_KEY_ID/SECRET/SESSION_TOKEN
            # |    3) shared files ~/.aws/credentials and ~/.aws/config (profiles, SSO, assume-role)
            # |    4) container credentials (ECS task role)  5) EC2 instance profile (IMDS).
            # | WHY it matters: locally you use (2) or (3). In AWS you should use an IAM ROLE
            # |    (4)/(5) so the app gets short-lived credentials from STS that rotate
            # |    automatically. Long-lived access keys in code or images are the classic WRONG
            # |    answer. The role needs least privilege, e.g. only bedrock:InvokeModel on the
            # |    specific model ARNs (the Converse API is authorized by that same
            # |    bedrock:InvokeModel permission).
            # |
            # | GOTCHA seen in this project: boto3.client(...) does NOT contact AWS or validate
            # |    credentials. It "succeeds" even with a blocked account. Failures (AccessDenied,
            # |    ValidationException) only appear on the first real API call.
            # +---------------------------------------------------------------------------------
            self.bedrock = boto3.client("bedrock-runtime", region_name=self.region)
            logger.info(f"✅ Bedrock provider initialized (region: {self.region})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Bedrock: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding from Bedrock Titan.

        An EMBEDDING is a list of numbers (a vector) that captures the MEANING of text. Texts with
        similar meaning get vectors that point in similar directions, which is what lets us find
        relevant documents without matching exact keywords.
        """
        # +- AWS EXAM [DVA-C02] ---------------------------------------------------------------
        # | Q: How do you call a Bedrock model with InvokeModel?
        # | A: invoke_model(modelId=..., body=<JSON string>), then json.loads(response["body"].read()).
        # | WHY: InvokeModel is the low-level call. The `body` format is DIFFERENT for every model
        # |    family (Titan wants "inputText"; Claude wants "messages"; ...), and the response
        # |    `body` is a streaming object you must .read() before parsing.
        # |
        # | "dimensions": 1024 -> Titan Text Embeddings V2 supports 256 / 512 / 1024. Smaller =
        # |    cheaper storage and faster search, slightly less accurate.
        # | "normalize": True  -> every vector has length 1, so the plain dot product used in
        # |    rag_core.search_authorized_docs EQUALS cosine similarity (range about -1 to 1).
        # |
        # | You must also have been granted ACCESS to the model in your account/Region, or the
        # |    call fails even with correct IAM permissions.
        # +-------------------------------------------------------------------------------------
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
        # This is the "A" (Augmented) in RAG: we paste the retrieved documents in front of the
        # question so the model answers from OUR data instead of from memory.
        user_message = f"Context:\n{context}\n\nQuestion: {question}"

        # +- AWS EXAM [DVA-C02] ---------------------------------------------------------------
        # | Q: InvokeModel or Converse for a chat app that may switch models?
        # | A: Converse.
        # | WHY: Converse uses ONE request/response shape for all supported chat models (system
        # |    prompt, messages, inferenceConfig), so changing `modelId` is the only edit. It also
        # |    handles multi-turn history and tool use consistently. InvokeModel needs a
        # |    model-specific body each time.
        # |
        # | inferenceConfig:
        # |    temperature 0.0 -> as deterministic as possible. Right for factual / compliance
        # |                       answers; higher values give more varied, creative text.
        # |    maxTokens 400   -> hard cap on output length. Cost control AND latency control.
        # |
        # | The model never "remembers" anything: every call is stateless, so we resend the
        # |    context each time. This is why RAG context is paid for as INPUT tokens.
        # +-------------------------------------------------------------------------------------
        response = self.bedrock.converse(
            modelId=self.chat_model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"temperature": 0.0, "maxTokens": 400},
        )

        answer = response["output"]["message"]["content"][0]["text"]
        # Bedrock reports exactly how many tokens were billed, so cost can be computed per request.
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

    # +- AWS EXAM [DVA-C02] -------------------------------------------------------------------
    # | Q: Your app gets intermittent ThrottlingException (HTTP 429) from an AWS API. What do you do?
    # | A: Retry with EXPONENTIAL BACKOFF and JITTER; request a quota increase if it is sustained.
    # | WHY: Retrying immediately in a tight loop makes throttling worse, and many clients that
    # |    all retry on the same schedule hit the service together again (a "retry storm").
    # |    Backoff (wait 1s, 2s, 4s, ...) spreads load out; jitter (a random offset) stops clients
    # |    from synchronizing. The AWS SDKs already do this for you: with boto3 you tune it via
    # |    botocore.config.Config(retries={"mode": "standard" or "adaptive", "max_attempts": N}).
    # |    Also know: 4xx errors other than throttling (AccessDenied, Validation) are NOT worth
    # |    retrying; 5xx and throttling are.
    # |
    # | This helper is the same idea written by hand for Gemini. Gemini TELLS us how long to wait
    # |    ("retry in 40s"), so we use that instead of a computed backoff. BedrockProvider has no
    # |    custom retry code, so it relies on boto3's built-in default retries.
    # +-----------------------------------------------------------------------------------------
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
    """Google Gemini provider (not AWS; same interface as BedrockProvider)."""

    def __init__(self):
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        # Models are configurable because providers retire them (gemini-2.0-flash and
        # text-embedding-004 both stopped working and had to be replaced).
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
        # (word count is only a rough proxy; real token counts are usually higher).
        input_tokens = len(context.split()) + len(question.split())
        output_tokens = len(answer.split())
        cost_usd = round(
            (input_tokens / 1_000_000) * self.input_cost_per_1m
            + (output_tokens / 1_000_000) * self.output_cost_per_1m,
            6,
        )
        return answer, input_tokens, output_tokens, cost_usd


class OpenAIProvider(LLMProvider):
    """OpenAI provider (not AWS; same interface as BedrockProvider)."""

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
        # OpenAI's chat API has no separate `system=` argument (Bedrock Converse and Gemini do);
        # the system prompt is the first message, with role "system".
        # (tests/test_llm_providers.py checks this with a fake client; no live OpenAI call was made.)
        response = self.client.chat.completions.create(
            model=self.chat_model,
            temperature=0.0,
            max_tokens=400,
            messages=[
                {"role": "system", "content": system_prompt},
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
    """
    Factory function to get the configured LLM provider.

    LLM_PROVIDER defaults to "bedrock". NOTE: the default means a machine with no LLM_PROVIDER set
    will try AWS first, which is why a missing/blocked AWS account shows up as an error here.
    """
    provider_name = os.getenv("LLM_PROVIDER", "bedrock").lower()

    if provider_name == "bedrock":
        return BedrockProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
