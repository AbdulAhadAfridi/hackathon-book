import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RAGChatbot from '../RAGChatbot';

// Mock fetch API
global.fetch = jest.fn();

describe('RAGChatbot', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders initial message', () => {
    render(<RAGChatbot />);

    expect(screen.getByText('Ask me anything about this book!')).toBeInTheDocument();
  });

  test('submits a question and shows loading state', async () => {
    // Mock successful API response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'This is a test response from the RAG system',
        sources: [{ url: 'http://example.com', heading: 'Example Source', section: 'Section 1', relevance_score: 0.8 }]
      })
    });

    render(<RAGChatbot />);

    const input = screen.getByPlaceholderText('Ask a question about the book content...');
    const button = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'What is this about?' } });
    fireEvent.click(button);

    // Check for loading state
    expect(screen.getByText('Thinking...')).toBeInTheDocument();

    // Wait for response to be displayed
    await waitFor(() => {
      expect(screen.getByText('This is a test response from the RAG system')).toBeInTheDocument();
    });
  });

  test('handles API error gracefully', async () => {
    // Mock API error
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: 'Internal server error' })
    });

    render(<RAGChatbot />);

    const input = screen.getByPlaceholderText('Ask a question about the book content...');
    const button = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'What is this about?' } });
    fireEvent.click(button);

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Failed to get response/)).toBeInTheDocument();
    });
  });

  test('validates input - empty query', async () => {
    render(<RAGChatbot />);

    const button = screen.getByText('Send');
    fireEvent.click(button);

    expect(screen.getByText('Please enter a question')).toBeInTheDocument();
  });

  test('validates input - long query', async () => {
    render(<RAGChatbot />);

    const input = screen.getByPlaceholderText('Ask a question about the book content...');
    const button = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'a'.repeat(1001) } }); // More than 1000 chars
    fireEvent.click(button);

    expect(screen.getByText('Query is too long. Please keep it under 1000 characters.')).toBeInTheDocument();
  });

  test('renders with custom backend URL', () => {
    render(<RAGChatbot backendUrl="https://api.example.com" />);

    expect(screen.getByText('Ask me anything about this book!')).toBeInTheDocument();
  });

  test('preserves user input during loading', async () => {
    // Create a promise that doesn't resolve immediately to simulate loading
    const pendingPromise = new Promise(() => {});
    fetch.mockReturnValueOnce(pendingPromise);

    render(<RAGChatbot />);

    const input = screen.getByPlaceholderText('Ask a question about the book content...');
    fireEvent.change(input, { target: { value: 'Test question' } });

    const button = screen.getByText('Send');
    fireEvent.click(button);

    // Input should still contain the value
    expect(input.value).toBe('Test question');
  });
});