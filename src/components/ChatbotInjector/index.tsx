import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import React, { useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import RAGChatbot from '@site/src/components/RAGChatbot';

export default function ChatbotInjector() {
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) {
      return undefined;
    }

    // Create a container for the chatbot
    const chatbotContainer = document.createElement('div');
    chatbotContainer.id = 'global-chatbot';
    document.body.appendChild(chatbotContainer);

    // Render the chatbot component
    const root = createRoot(chatbotContainer);
    root.render(<RAGChatbot />);

    // Clean up on unmount
    return () => {
      root.unmount();
      if (chatbotContainer.parentNode) {
        chatbotContainer.parentNode.removeChild(chatbotContainer);
      }
    };
  }, []);

  return null;
}