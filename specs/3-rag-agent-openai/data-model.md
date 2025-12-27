# Data Models: RAG Agent Integration

## Core Entities

### Agent Configuration
- **Fields**:
  - `openai_api_key`: str (required) - OpenAI API key for authentication
  - `model`: str (default: "gpt-4-turbo") - OpenAI model to use for generation
  - `system_prompt`: str - System prompt that enforces grounding in retrieved content
- **Relationships**: Uses Config class for loading from environment variables
- **Validation**: Requires valid OpenAI API key

### Retrieval Context
- **Fields**:
  - `query`: str - Original user query
  - `results`: List[SearchResult] - Retrieved content chunks from Qdrant
  - `query_embedding`: List[float] - Generated embedding for the query
  - `execution_time`: float - Time taken for retrieval
- **Relationships**: Composed of SearchResult objects from existing retrieval pipeline
- **Validation**: Must have non-empty results list when retrieval is successful

### User Query
- **Fields**:
  - `query`: str - Text of the user's question
  - `top_k`: int (default: 5) - Number of results to retrieve
  - `user_provided_text`: Optional[str] - Text provided by user for context (for User Story 2)
- **Relationships**: Input to both retrieval and generation processes
- **Validation**: Query must be non-empty and not exceed maximum length

### Agent Response
- **Fields**:
  - `query`: str - Original user query
  - `answer`: str - Generated answer based on retrieved context
  - `retrieved_context`: RetrievalResponse - Context used to generate the answer
  - `usage`: dict - Token usage information from OpenAI API
  - `model`: str - Model used for generation
- **Relationships**: Composed of retrieved context and generated answer
- **Validation**: Answer must be grounded in retrieved context; citations should be present

## State Transitions

### Query Processing Flow
1. **User Query Received** → Input validation
2. **Validated Query** → Context retrieval from Qdrant
3. **Retrieved Context** → Formatted for agent consumption
4. **Formatted Context** → OpenAI API call with system prompt
5. **API Response** → Response validation and formatting
6. **Validated Response** → Return to user

### Error Handling States
- **API Key Missing**: Configuration error, cannot proceed
- **Retrieval Failed**: Return error message to user
- **Context Empty**: Return message indicating insufficient information
- **Generation Failed**: Return error message to user

## Validation Rules

### From Requirements
- **FR-003**: Agent responses must be based only on retrieved context
- **FR-004**: Responses must include proper citations to source material
- **FR-005**: Must handle user-provided text selections
- **FR-008**: Must handle error conditions gracefully

### Data Integrity
- All text fields must be properly sanitized
- Embedding vectors must have correct dimensions (1024 for Cohere)
- Score values must be within valid range (0.0 to 1.0)
- API usage data must be properly formatted