# Container image for the FastAPI service.
#
# +- AWS EXAM [CLF-C02 / DVA-C02] -------------------------------------------------------------
# | Q: How do you run this container on AWS with the least operational work?
# | A: Push the image to Amazon ECR (private container registry), then run it on AWS App Runner
# |    (simplest: it builds/scales/load-balances for you) or on ECS with Fargate (more control,
# |    still serverless: no EC2 instances to manage).
# | WHY: Both are managed container services. App Runner = "give me a URL for my container".
# |    ECS/Fargate = you define tasks/services/networking. EC2 would mean YOU patch and scale the
# |    servers. Permissions to call Bedrock come from the service's IAM ROLE (App Runner "instance
# |    role" / ECS "task role"), never from access keys baked into this image.
# | Also: keep images small and secret-free; anything COPY'd or ENV'd here is readable by anyone
# |    who can pull the image.
# +-------------------------------------------------------------------------------------------
#
# NOTE: every module rag_app.py imports must be copied (rag_core, llm_provider, documents and the
# docs_extra_* data files), plus embeddings/ so startup loads precomputed vectors instead of
# calling the embedding API. A missing file shows up as ModuleNotFoundError when the container starts.
# requirements.txt holds runtime dependencies only (no pytest/deepeval), which is right for an image.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag_app.py rag_core.py llm_provider.py workflow.py documents.py docs_extra_*.py streamlit_app.py ./
COPY embeddings/ ./embeddings/
COPY static/ ./static/

EXPOSE 8080

CMD ["uvicorn", "rag_app:app", "--host", "0.0.0.0", "--port", "8080"]
