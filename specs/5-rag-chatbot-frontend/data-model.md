# Data Models: RAG Chatbot in Book Frontend

## Core Entities

### ChatMessage
- **Fields**:
  - `id`: string (required) - Unique identifier for the message
  - `content`: string (required) - Text content of the message
  - `sender`: 'user' | 'bot' (required) - Indicates message origin
  - `timestamp`: Date (required) - When the message was created
  - `status`: 'sent' | 'pending' | 'error' (default: 'sent') - Message delivery status
- **Validation**: Content must be non-empty, sender must be one of allowed values
- **Relationships**: Part of a ChatConversation

### ChatQuery
- **Fields**:
  - `query`: string (required) - The user's question to send to the backend
  - `selectedText`: string | null (optional) - Optional context from the current page
- **Validation**: Query must be non-empty and not exceed maximum length
- **Relationships**: Sent to backend API to generate ChatResponse

### ChatResponse
- **Fields**:
  - `answer`: string (required) - The answer from the RAG system
  - `sources`: Array<{url: string, section: string, heading: string, relevance_score: number}> (optional) - Citations to source material
  - `processing_time`: number (optional) - Time taken to process the query
  - `timestamp`: string (optional) - When the response was generated
  - `query_id`: string (optional) - Identifier for the original query
- **Validation**: Answer must be non-empty when status is success
- **Relationships**: Generated in response to a ChatQuery

## State Transitions

### Message Lifecycle
1. **User Input** → Message created with `status: 'pending'`
2. **API Request Sent** → Message status remains `pending`, loading indicator shown
3. **API Response Received** → Message updated with `status: 'sent'` and bot response added
4. **API Error** → Message updated with `status: 'error'` and error message

### Component State Flow
- **Initial State**: `messages: []`, `isLoading: false`, `error: null`
- **Query Submitted**: `isLoading: true`, user message added with `pending` status
- **Response Received**: `isLoading: false`, bot response added to messages
- **Error Occurred**: `isLoading: false`, error state updated

## Validation Rules

### From Requirements
- **FR-003**: Responses must be displayed in a user-friendly chat interface
- **FR-004**: API communication errors must be handled gracefully with user feedback
- **FR-007**: Loading states must be provided during query processing
- **FR-008**: User input must be preserved in case of temporary connection failures

### Data Integrity
- All text fields must be properly sanitized to prevent XSS
- Message IDs must be unique within the conversation
- Timestamps must be in valid ISO format
- Query length must be within API limits (e.g., < 1000 characters)