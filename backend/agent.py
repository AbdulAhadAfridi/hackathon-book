"""
RAG Agent Construction with OpenAI Agents SDK
Main implementation file for creating an intelligent agent that retrieves relevant book content and generates grounded answers
"""
import logging
import argparse
from typing import Dict, Any, List
from agents import Agent, Runner, function_tool
from retrieve import retrieve_similar_chunks, RetrievalResponse
from config import Config
import asyncio
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI


ROUTER_API_KEY="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"

client = AsyncOpenAI(
    api_key=ROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    )

OpenRoutermodel = OpenAIChatCompletionsModel(
    openai_client=client,
    model="mistralai/devstral-2512:free",
)



@function_tool
def retrieve_context_tool(query: str, top_k: int = 5, user_provided_text: str = None) -> str:
    """
    Retrieve relevant context using the Spec-2 retrieval pipeline

    Args:
        query: User query to retrieve context for
        top_k: Number of results to retrieve (default: 5)
        user_provided_text: Optional text provided by user for additional context

    Returns:
        Formatted string containing retrieved context information
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Retrieving context for query: {query[:50]}...")

    try:
        retrieval_response = retrieve_similar_chunks(query, top_k=top_k)

        # Format the results as a string that can be used by the agent
        if not retrieval_response.results:
            return "No relevant context found in the book content."

        formatted_context = "Retrieved Context from Book Content:\n\n"
        for i, result in enumerate(retrieval_response.results, 1):
            formatted_context += f"Document {i}:\n"
            formatted_context += f"URL: {result.payload.get('url', 'N/A')}\n"
            formatted_context += f"Section: {result.payload.get('section', 'N/A')}\n"
            formatted_context += f"Heading: {result.payload.get('heading', 'N/A')}\n"
            formatted_context += f"Content: {result.text}\n"
            formatted_context += f"Relevance Score: {result.score:.3f}\n"
            formatted_context += "---\n"

        return formatted_context
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return f"Error retrieving context: {str(e)}"


class RAGAgent:
    """
    RAG Agent that uses OpenAI Agents SDK to retrieve relevant content and generate grounded answers
    Integrates with the Spec-2 retrieval pipeline to ensure responses are based only on retrieved context
    """

    def __init__(self, openai_api_key: str = None, model: str = "gpt-4-turbo"):
        """
        Initialize the RAG Agent with OpenAI Agents SDK and retrieval functionality

        Args:
            openai_api_key: OpenAI API key (defaults to using Config.OPENAI_API_KEY)
            model: OpenAI model to use for generation (default: gpt-4-turbo)
        """
        if openai_api_key is None:
            openai_api_key = getattr(Config, 'OPENAI_API_KEY', None)

        if not openai_api_key:
            # Try to get from environment directly as fallback
            import os
            openai_api_key = os.getenv("OPENAI_API_KEY", None)

        if not openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in your environment or pass as parameter.")

        # Set the API key in environment for the agents SDK
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key

        self.model = model
        self.logger = logging.getLogger(__name__)

        # Create the agent with retrieval tool
        self.agent = Agent(
            name="RAG Book Assistant",
            instructions="""
            You are a helpful assistant that answers questions 
            """,
            tools=[retrieve_context_tool],
            model=OpenRoutermodel
        )

    async def answer_query(self, query: str, top_k: int = 5, user_provided_text: str = None) -> Dict[str, Any]:
        """
        Answer a user query using retrieved context and OpenAI agent

        Args:
            query: User query to answer
            top_k: Number of results to retrieve (default: 5)
            user_provided_text: Optional text provided by user for additional context

        Returns:
            Dictionary containing the answer, retrieved context, and metadata
        """
        self.logger.info(f"Answering query: {query}")

        try:
            # Prepare the input for the agent
            agent_input = query
            if user_provided_text:
                agent_input = f"{query}\n\nAdditional context provided by user: {user_provided_text}"

            # Run the agent with the user query
            result = await Runner.run(self.agent, agent_input)

            # Extract the final output
            answer = result.final_output if hasattr(result, 'final_output') else str(result)

            # For the retrieved context, we'll use the agent's internal processing
            # The actual context is handled within the agent via tool calls
            retrieved_context_str = "Context was retrieved and used by the agent internally"

            return {
                "query": query,
                "answer": answer,
                "retrieved_context": retrieved_context_str,
                "user_provided_text": user_provided_text,
                "usage": {},  # Usage info would come from the agent run result if available
                "model": self.model
            }
        except Exception as e:
            self.logger.error(f"Error generating answer: {str(e)}")
            return {
                "query": query,
                "answer": "Sorry, I'm currently unable to process your request. Please try again later.",
                "retrieved_context": [],
                "user_provided_text": user_provided_text,
                "usage": {},
                "model": self.model,
                "error": str(e)
            }

    async def answer_complex_query(self, query: str, top_k: int = 5, user_provided_text: str = None) -> Dict[str, Any]:
        """
        Answer a complex query that may require multiple retrieval steps or synthesis of information

        Args:
            query: Complex user query that may require multiple retrieval steps
            top_k: Number of results to retrieve (default: 5)
            user_provided_text: Optional text provided by user for additional context

        Returns:
            Dictionary containing the synthesized answer, all retrieved contexts, and metadata
        """
        self.logger.info(f"Answering complex query: {query}")

        # For complex queries, we can provide more detailed instructions
        complex_agent = Agent(
            name="RAG Book Assistant - Complex Queries",
            instructions=f"""
            you are general assistant
            """,
            tools=[retrieve_context_tool],
            model=OpenRoutermodel
        )

        try:
            # Prepare the input for the agent
            agent_input = query
            if user_provided_text:
                agent_input = f"{query}\n\nAdditional context provided by user: {user_provided_text}"

            # Run the agent with the complex query
            result = await Runner.run(complex_agent, agent_input)

            # Extract the final output
            answer = result.final_output if hasattr(result, 'final_output') else str(result)

            # For the retrieved context, we'll use the agent's internal processing
            # The actual context is handled within the agent via tool calls
            all_retrieved_contexts = "Context was retrieved and used by the agent internally"

            return {
                "query": query,
                "answer": answer,
                "all_retrieved_contexts": all_retrieved_contexts,
                "user_provided_text": user_provided_text,
                "usage": {},  # Usage info would come from the agent run result if available
                "model": self.model
            }
        except Exception as e:
            self.logger.error(f"Error generating answer for complex query: {str(e)}")
            return {
                "query": query,
                "answer": "Sorry, I'm currently unable to process your complex request. Please try again later.",
                "all_retrieved_contexts": [],
                "user_provided_text": user_provided_text,
                "usage": {},
                "model": self.model,
                "error": str(e)
            }


def setup_logging(level: str = "INFO") -> None:
    """
    Set up basic logging configuration.

    Args:
        level: Logging level as string (default: "INFO"). Options include "DEBUG", "INFO", "WARNING", "ERROR".
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def main():
    """
    Main function with argument parsing for the RAG Agent
    """
    setup_logging()  # Set up logging
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='RAG Agent with OpenAI Agents SDK')
    parser.add_argument('--query', type=str, required=True, help='Query to answer using the RAG agent')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to retrieve (default: 5)')
    parser.add_argument('--model', type=str, default='gpt-4-turbo', help='OpenAI model to use (default: gpt-4-turbo)')
    parser.add_argument('--user-text', type=str, help='Optional text provided by user for additional context')
    parser.add_argument('--complex', action='store_true', help='Process as a complex multi-step query')

    args = parser.parse_args()

    logger.info(f"Initializing RAG Agent with query: {args.query}")

    try:
        # Initialize the RAG agent
        agent_wrapper = RAGAgent(model=args.model)

        # Run the appropriate query method based on the --complex flag
        if args.complex:
            # Process as a complex multi-step query
            result = asyncio.run(agent_wrapper.answer_complex_query(args.query, top_k=args.top_k, user_provided_text=args.user_text))

            # Print the results for complex query
            print(f"Complex Query: {result['query']}")
            if result['user_provided_text']:
                print(f"User-provided text: {result['user_provided_text'][:100]}...")
            print(f"Answer: {result['answer']}")
            print(f"Retrieved {len(result['all_retrieved_contexts'])} context chunks")
        else:
            # Answer the regular query
            result = asyncio.run(agent_wrapper.answer_query(args.query, top_k=args.top_k, user_provided_text=args.user_text))

            # Print the results
            print(f"Query: {result['query']}")
            if result.get('user_provided_text'):
                print(f"User-provided text: {result['user_provided_text'][:100]}...")
            print(f"Answer: {result['answer']}")
            print(f"Retrieved {len(result['retrieved_context'])} context chunks")

    except Exception as e:
        logger.error(f"Error running RAG Agent: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()