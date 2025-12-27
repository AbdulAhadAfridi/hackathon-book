# Quickstart: RAG Chatbot in Book Frontend

## Prerequisites

- Node.js 16+ and npm/yarn
- Docusaurus 3.x project
- Running FastAPI backend with RAG agent (localhost:8000)

## Installation

### 1. Component Setup

Place the RAGChatbot component in your Docusaurus project:

```bash
# Create the components directory if it doesn't exist
mkdir -p src/components

# The RAGChatbot.jsx file should be placed in src/components/
```

### 2. Backend Configuration

Ensure your FastAPI backend has CORS configured to allow requests from your frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Usage

### 1. Basic Integration

Import and use the RAGChatbot component in your .mdx files:

```jsx
import RAGChatbot from '@site/src/components/RAGChatbot';

# Your Book Page Title

Here's some content in your book.

<RAGChatbot />
```

### 2. Configuration Options

The component can be configured with the following props:

```jsx
<RAGChatbot
  backendUrl="https://your-backend-url.com"  // Default: http://localhost:8000
  pageTitle="Current Page Title"            // Optional: context about current page
  initialMessage="Ask me anything about this book!" // Optional: welcome message
/>
```

### 3. Styling

The component uses CSS modules for styling. You can customize the appearance by modifying the CSS classes in the component's stylesheet.

## Examples

### Basic Usage
```jsx
<RAGChatbot />
```

### With Custom Backend URL
```jsx
<RAGChatbot backendUrl="https://api.yourbook.com" />
```

### With Page Context
```jsx
<RAGChatbot pageTitle="Introduction to RAG Systems" />
```

## Testing

### 1. Manual Testing

1. Start your Docusaurus development server: `npm run start`
2. Navigate to a page containing the RAGChatbot component
3. Type a question and submit it
4. Verify that you receive a response from the backend

### 2. Component Testing

Run the component tests:
```bash
npm test -- src/components/__tests__/RAGChatbot.test.jsx
```

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Ensure your backend allows requests from your frontend domain
2. **API Unreachable**: Check that your backend is running and accessible at the configured URL
3. **Component Not Loading**: Verify the component file is in the correct location and properly imported
4. **Styling Conflicts**: Check that CSS modules are properly configured and not conflicting with Docusaurus styles

### Verification Steps:

1. Test backend connectivity:
   ```bash
   curl http://localhost:8000/health
   ```

2. Test API endpoint directly:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
        -H "Content-Type: application/json" \
        -d '{"query": "test query", "selected_text": null}'
   ```

3. Check browser console for any JavaScript errors or network issues