import React, { useState, useRef, useEffect } from 'react';
import styles from './RAGChatbot.module.css';

// Define TypeScript-like interfaces using JSDoc
/**
 * @typedef {Object} ChatMessage
 * @property {string} id - Unique identifier for the message
 * @property {string} content - Text content of the message
 * @property {'user' | 'bot'} sender - Indicates message origin
 * @property {Date} timestamp - When the message was created
 * @property {'sent' | 'pending' | 'error'} [status='sent'] - Message delivery status
 */

/**
 * @typedef {Object} ChatQuery
 * @property {string} query - The user's question to send to the backend
 * @property {string | null} [selectedText] - Optional context from the current page
 */

/**
 * @typedef {Object} ChatResponse
 * @property {string} response - The answer from the RAG system
 * @property {Array<{url: string, section: string, heading: string, relevance_score: number}>} [sources] - Citations to source material
 * @property {number} [processing_time] - Time taken to process the query
 * @property {string} [timestamp] - When the response was generated
 * @property {string} [query_id] - Identifier for the original query
 */

/**
 * RAG Chatbot Component
 * A React component that allows users to ask questions about book content and receive answers from a RAG system
 * @param {Object} props
 * @param {string} [props.backendUrl='http://localhost:8000'] - URL of the backend API
 * @param {string} [props.pageTitle] - Title of the current page (for context)
 * @param {string} [props.initialMessage] - Initial welcome message
 */
const RAGChatbot = ({
  backendUrl = 'http://localhost:8000',
  pageTitle,
  initialMessage = 'Ask me anything about this book!'
}) => {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  // Add initial message when component mounts
  useEffect(() => {
    if (initialMessage) {
      setMessages([{
        id: 'initial-' + Date.now(),
        content: initialMessage,
        sender: 'bot',
        timestamp: new Date(),
        status: 'sent'
      }]);
    }
  }, [initialMessage]);

  // Scroll to bottom of messages when they change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Sanitize input to prevent XSS
   * @param {string} str
   * @return {string}
   */
  const sanitizeInput = (str) => {
    if (typeof str !== 'string') return '';
    return str.replace(/</g, '&lt;').replace(/>/g, '&gt;');
  };

  /**
   * Generate a unique ID
   * @return {string}
   */
  const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  };

  /**
   * Handle user input submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) {
      setError('Please enter a question');
      return;
    }

    if (inputValue.trim().length > 1000) {
      setError('Query is too long. Please keep it under 1000 characters.');
      return;
    }

    setError(null);
    setIsLoading(true);

    // Add user message to the conversation
    const userMessage = {
      id: generateId(),
      content: sanitizeInput(inputValue),
      sender: 'user',
      timestamp: new Date(),
      status: 'pending'
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');

    try {
      // Call the backend API
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: currentInput,
          selected_text: null  // Could be enhanced to include page context
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response to the conversation
      const botMessage = {
        id: generateId(),
        content: data.response,
        sender: 'bot',
        timestamp: new Date(),
        status: 'sent'
      };

      // Update the user message status to 'sent' and add bot response
      setMessages(prev => {
        const updatedMessages = prev.map(msg =>
          msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
        );
        return [...updatedMessages, botMessage];
      });
    } catch (err) {
      console.error('Error communicating with backend:', err);

      // Update the user message status to 'error'
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessage.id ? { ...msg, status: 'error' } : msg
        )
      );

      setError(`Failed to get response: ${err.message}. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        RAG Chatbot
      </div>

      <div className={styles.chatArea}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.botMessage}`}
          >
            {message.content}
            {message.sender === 'bot' && message.status === 'sent' && (
              <div className={styles.sourceCitation}>
                {message.sources && message.sources.length > 0 && (
                  <>
                    Sources: {message.sources.slice(0, 3).map((source, idx) => (
                      <span key={idx}>
                        <a href={source.url} target="_blank" rel="noopener noreferrer">
                          {source.heading || 'Source'}
                        </a>
                        {idx < message.sources.length - 1 && ', '}
                      </span>
                    ))}
                  </>
                )}
              </div>
            )}
            {message.status === 'error' && (
              <div className={styles.error}>Failed to send message</div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className={styles.message + ' ' + styles.botMessage}>
            <div className={styles.loading}>Thinking...</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className={styles.error}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.inputArea}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about the book content..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default RAGChatbot;