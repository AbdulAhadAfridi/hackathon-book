# Agent Context: RAG System (Ingestion + Retrieval + Agent + API + Frontend)

## Project Overview
- **Feature**: 1-rag-ingestion-pipeline, 2-retrieval-validation, 3-rag-agent-openai, 4-fastapi-backend-frontend, 5-rag-chatbot-frontend
- **Purpose**: Complete RAG system with ingestion, retrieval, AI agent, API layer, and frontend chatbot for book content
- **Technology Stack**: Python, OpenAI API, Cohere API, Qdrant Cloud, FastAPI, React, Docusaurus, requests, BeautifulSoup

## Key Components

### Ingestion Pipeline (Feature 1)
- **main.py**: Main ingestion pipeline orchestrating URL fetching → chunking → embedding → storage
- **Web Crawling**: Uses requests with robots.txt respect and rate limiting
- **Content Extraction**: Uses BeautifulSoup to extract clean text from Docusaurus sites
- **Chunking**: Recursive character splitting with 1000 char chunks and 100 char overlap
- **Embeddings**: Cohere's embed-english-v3.0 model
- **Storage**: Qdrant Cloud vector database with metadata

### Retrieval Pipeline (Feature 2)
- **retrieve.py**: Main retrieval pipeline with Cohere embeddings and Qdrant vector store
- **CohereEmbeddingClient**: Interface for generating embeddings with caching and retry logic
- **QdrantVectorStore**: Interface for similarity search in Qdrant
- **Data Models**: SearchResult, RetrievalRequest, RetrievalResponse for structured data handling

### Agent Integration (Feature 3)
- **agent.py**: Main RAG agent implementation using OpenAI Agents SDK
- **RAGAgent**: Class that integrates OpenAI SDK with retrieval pipeline
- **Grounding Enforcement**: System prompts that enforce responses based only on retrieved context
- **Context Formatting**: Proper formatting of retrieved context for agent consumption

### API Layer (Feature 4)
- **api.py**: Main FastAPI application with CORS configuration and chat endpoint
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints
- **CORS Middleware**: Cross-Origin Resource Sharing configuration for frontend access
- **Request/Response Models**: Pydantic models for request validation and response structuring
- **RAG Agent Integration**: Proper integration with the existing RAG agent for query processing

### Frontend Chatbot (Feature 5)
- **RAGChatbot.jsx**: React component for embedding RAG chat functionality in Docusaurus book pages
- **React**: Component-based UI library for building user interfaces
- **Docusaurus Integration**: Seamless embedding in .mdx pages with theme consistency
- **API Communication**: Fetch API for communicating with backend services
- **State Management**: React hooks for managing chat state, loading, and error conditions

## Configuration
- **Environment Variables**: OPENAI_API_KEY, COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY
- **Command Line Args**: --query, --top-k, --model (for agent); --website-url, --chunk-size, --chunk-overlap, --max-pages (for ingestion)
- **Default Values**: chunk_size=1000, chunk_overlap=100, max_pages=1000, top_k=5, model=gpt-4-turbo

## Data Models
### Ingestion
- **ContentDocument**: Extracted content with URL, title, content, headings, section
- **ContentChunk**: Chunked content with metadata for embedding
- **EmbeddingRecord**: Vector embeddings with metadata stored in Qdrant
- **CrawlSession**: Tracks crawl session progress and results

### Retrieval
- **SearchResult**: Represents a single search result from Qdrant similarity search
- **RetrievalRequest**: Represents a request for content retrieval from the vector store
- **RetrievalResponse**: Represents the response from a content retrieval request

### Agent
- **Agent Configuration**: Settings that define the agent's behavior, including OpenAI model selection, system prompts, and integration parameters
- **Retrieval Context**: The set of documents or text snippets retrieved from book content that form the basis for the agent's response
- **User Query**: The input from the user that triggers the retrieval and response generation process
- **Agent Response**: The output from the agent, including the answer and citations to source material

## API Contracts
### Ingestion Pipeline
- **crawl_website()**: Discovers and returns pages from website
- **extract_content()**: Extracts clean text from HTML page
- **chunk_content()**: Splits content into appropriately sized chunks
- **generate_embeddings()**: Creates embeddings using Cohere API
- **store_embeddings()**: Stores embeddings in Qdrant with metadata
- **main()**: Orchestrates the complete pipeline

### Retrieval Pipeline
- **retrieve_similar_chunks()**: Retrieve similar content chunks from Qdrant based on semantic similarity
- **validate_pipeline()**: Validate the retrieval pipeline with test query
- **run_integration_tests()**: Perform final integration testing of the retrieval pipeline

### Agent Integration
- **RAGAgent.__init__()**: Initialize the RAG Agent with OpenAI client and retrieval functionality
- **RAGAgent.retrieve_context()**: Retrieve relevant context using the Spec-2 retrieval pipeline
- **RAGAgent.format_context_for_agent()**: Format retrieved context into a string for the OpenAI agent
- **RAGAgent.answer_query()**: Answer a user query using retrieved context and OpenAI agent

### API Layer
- **POST /api/chat**: Process user chat queries and return responses from RAG agent
- **GET /health**: Check the health status of the API
- **Request Models**: ChatRequest with query and optional selected_text
- **Response Models**: ChatResponse with answer, sources, and metadata
- **Error Handling**: Structured error responses with appropriate HTTP status codes

### Frontend Integration
- **RAGChatbot Component**: Embeddable React component for Docusaurus .mdx pages
- **API Communication**: POST requests to /api/chat with user queries
- **State Management**: Loading states, error handling, and message history
- **Styling**: CSS modules for theme-consistent appearance
- **Props Interface**: Configurable backend URL, page context, and initial messages

## Error Handling
- Comprehensive error handling with retry logic across all components
- Individual failures don't stop entire pipeline
- Detailed logging for debugging
- Summary reports of failures at completion
- API key validation and connection checks
- Graceful degradation when retrieval fails

## Success Criteria
### Ingestion Pipeline
- 95% URL discovery success rate
- 98% content extraction accuracy
- 99% embedding generation success rate
- 99% storage success rate
- Process 100 pages within 10 minutes
- Idempotent operation (no duplicates on re-run)

### Retrieval Pipeline
- Query embeddings generated consistently with Spec 1
- Relevant chunks retrieved from Qdrant for test queries
- Retrieved results include correct text and metadata
- Similarity scores reflect semantic relevance
- Pipeline failures are detectable and debuggable

### Agent Integration
- Agent instantiated using OpenAI Agents SDK
- Retrieval tool integrates with Spec-2 retrieval pipeline
- Agent answers questions using retrieved context only
- Agent provides proper citations to source material
- Responses are coherent, relevant, and citation-ready
- Complex multi-step queries handled correctly in 80% of cases

### API Layer
- FastAPI server starts successfully and exposes chat endpoints
- Frontend can send user queries and selected text to the backend
- Backend routes queries through the RAG agent and returns responses
- API responses are structured, low-latency, and reliable
- Local development workflow is stable and reproducible
- CORS configured properly for frontend access

### Frontend Integration
- RAGChatbot component embeds seamlessly in Docusaurus .mdx pages
- Component communicates with backend API to process user queries
- User interface provides loading states and error handling
- Chat interface displays responses with proper formatting and citations
- Component maintains visual consistency with Docusaurus theme
- Lightweight implementation with minimal impact on page load times