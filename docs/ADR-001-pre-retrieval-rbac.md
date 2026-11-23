# ADR-001: Pre-Retrieval RBAC Metadata Filtering for Enterprise RAG

- **Status:** Accepted
- **Date:** 2026-11-23
- **Context:** Enterprise AI Knowledge Assistant (AWS Bedrock + Vector Search)

---

## 1. Problem Statement
An internal RAG assistant must index documents across multiple sensitivity tiers (`employee`, `engineering`, `hr`, `executive`). If an unauthorized user asks about confidential data—or uses prompt injection to impersonate an executive—the system must guarantee **zero leakage** while maintaining low latency and high recall.

## 2. Options Considered
1. **Post-Retrieval Filtering:** Filter top-k results *after* vector search. Rejected due to severe recall degradation when restricted docs crowd out authorized docs at top-k.
2. **Separate Vector Indexes per Role:** Physical silos per role. Rejected due to combinatorial explosion and duplicated embeddings for shared company policies.
3. **Pre-Retrieval Metadata Filtering (Chosen):** Store one copy of each chunk with `allowed_roles` metadata and apply a hard permission predicate *before* similarity scoring (`WHERE $user_role = ANY(allowed_roles)`).

## 3. Decision & Scaling Plan
Adopt **Pre-Retrieval Metadata Filtering** paired with an upstream **Adversarial Triage Router** and a **0.35 cosine similarity floor**, enforced continuously via DeepEval, Promptfoo, and Playwright in GitHub Actions. Production scale path: **Amazon RDS PostgreSQL (`pgvector` 0.8+)** + **Amazon Cognito JWT claims**.
