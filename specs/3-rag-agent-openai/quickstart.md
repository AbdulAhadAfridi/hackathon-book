# Quickstart: RAG Agent Integration

## Prerequisites

- Python 3.11+
- OpenAI API key
- Access to Qdrant vector database (from Spec-1 ingestion)
- Access to Cohere API key (from Spec-1 ingestion)

## Setup

### 1. Environment Configuration

Set up your environment variables in a `.env` file in the backend directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the agent from the command line:

```bash
cd backend
python agent.py --query "What is the main concept of the book?"
```

#### Additional Options:

```bash
# Specify number of results to retrieve
python agent.py --query "What are the key principles?" --top-k 3

# Use a different OpenAI model
python agent.py --query "Explain the methodology" --model "gpt-3.5-turbo"

# Include user-provided text for additional context
python agent.py --query "Based on this text, explain the implications?" --user-text "Here is the specific text I'm referring to..."

# Process as a complex multi-step query
python agent.py --query "Provide a comprehensive analysis of all aspects..." --complex

# Combine all options
python agent.py --query "How does the system work?" --top-k 5 --model "gpt-4-turbo" --complex
```

### Python Library Usage

You can also use the agent as a library:

```python
from agent import RAGAgent

# Initialize the agent
agent = RAGAgent(openai_api_key="your-api-key")

# Ask a basic question
result = agent.answer_query("What does the book say about AI agents?")

print(result["answer"])
print(f"Retrieved {len(result['retrieved_context'].results)} context chunks")

# Ask a question with user-provided text
result = agent.answer_query(
    query="Based on this text, what are the implications?",
    user_provided_text="Here is the specific text I'm referring to..."
)

print(result["answer"])

# Process a complex multi-step query
result = agent.answer_complex_query("Provide a comprehensive analysis of all aspects...")

print(result["answer"])
print(f"Used {result['iterations_used']} retrieval iterations")
```

## Examples

### Basic Query
```bash
python agent.py --query "What are the main topics covered in the book?"
```

### Query with User-Provided Context
```bash
python agent.py --query "What are your thoughts on this specific section?" --user-text "This is the text section I'm asking about..."
```

### Complex Multi-Step Query
```bash
python agent.py --query "Explain the relationship between RAG and LLMs in this context" --complex
```

## Troubleshooting

### Common Issues:

1. **API Key Errors**: Ensure all required API keys are set in your environment
2. **Connection Issues**: Verify Qdrant URL and API key are correct
3. **Rate Limiting**: If you encounter rate limit errors, implement appropriate delays
4. **Empty Results**: If retrieval returns no results, verify the Qdrant collection has data

### Verification Steps:

1. Test the retrieval pipeline independently:
   ```bash
   python retrieve.py --query "test query"
   ```

2. Verify the agent can be imported:
   ```bash
   python -c "from agent import RAGAgent; print('Success')"
   ```

## Performance Tips

- Use `--top-k` parameter to control the number of retrieved results (default is 5)
- Choose appropriate models based on your needs (gpt-3.5-turbo for speed, gpt-4-turbo for quality)
- Monitor token usage as longer contexts consume more tokens
- Consider caching strategies for frequently asked questions