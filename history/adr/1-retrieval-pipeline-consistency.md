# ADR-1: Retrieval Pipeline Consistency

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-25
- **Feature:** retrieval-validation
- **Context:** Need to ensure consistency between the ingestion and retrieval pipelines for the RAG system, specifically using the same Cohere embedding model and Qdrant vector database to maintain semantic compatibility.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- Embedding Model: Cohere embed-english-v3.0 (1024-dimensional vectors)
- Vector Database: Qdrant Cloud with cosine similarity search
- Consistency Approach: Use identical embedding generation process for both ingestion and retrieval
- Vector Dimensions: Maintain 1024-dimensional vectors across both pipelines
- Metadata Schema: Preserve consistent metadata structure (URL, section, heading, chunk_index)

## Consequences

### Positive

- Semantic compatibility between stored and queried embeddings
- Reduced complexity by reusing existing infrastructure and configuration
- Consistent performance characteristics between ingestion and retrieval
- Simplified maintenance with single embedding model to manage
- Lower risk of vector dimension mismatches during retrieval

### Negative

- Tight coupling between ingestion and retrieval components
- Potential vendor lock-in to Cohere embedding model
- Limited flexibility to optimize retrieval with different models
- Any changes to embedding model affect both pipelines simultaneously

## Alternatives Considered

Alternative A: Different embedding models for ingestion vs. retrieval
- Would allow optimization of each pipeline independently
- Would increase complexity and risk of incompatibility
- Rejected due to potential semantic mismatch issues

Alternative B: Multiple embedding models with fallback approach
- Would provide flexibility and redundancy
- Would increase storage requirements and query complexity
- Rejected due to added complexity without clear benefit

Alternative C: Local embedding models instead of Cohere
- Would reduce vendor dependency
- Would increase operational complexity and computational requirements
- Rejected due to infrastructure overhead

## References

- Feature Spec: specs/retrieval-validation/spec.md
- Implementation Plan: specs/retrieval-validation/plan.md
- Related ADRs: None
- Evaluator Evidence: history/prompts/retrieval-validation/1-retrieval-pipeline-validation-spec.spec.prompt.md