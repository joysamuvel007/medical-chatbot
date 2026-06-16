
import { useState, useCallback, useRef } from 'react';
import { sendMessage, checkHealth, clearSession } from '../utils/api';

export function useChat() {

  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm your healthcare assistant. I can help you with health questions, symptoms, wellness advice, and more. How can I assist you today?\n\n⚠️ Note: I provide general health information only. Always consult a qualified healthcare professional for medical advice.",
      intent: 'greeting',
      emergencyLevel: 0,
      emergencyMessage: null,
      sources: [],
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  const messagesEndRef = useRef(null);

  const nextId = useRef(1);
  const getId = () => `msg-${nextId.current++}`;

  const send = useCallback(async (userText) => {
    if (!userText.trim() || isLoading) return;

    const userMsg = {
      id: getId(),
      role: 'user',
      content: userText,
      intent: null,
      emergencyLevel: 0,
      sources: [],
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const data = await sendMessage(userText, sessionId);

      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
      }

      const botMsg = {
        id: getId(),
        role: 'assistant',
        content: data.response,
        intent: data.intent,
        emergencyLevel: data.emergency_level,
        emergencyMessage: data.emergency_message,
        sources: data.sources || [],
        confidence: data.confidence,
        isSafe: data.is_safe,
      };

      setMessages(prev => [...prev, botMsg]);

    } catch (err) {
      const errMsg = {
        id: getId(),
        role: 'assistant',
        content: `⚠️ Error: ${err.message}. Please ensure the backend server is running on port 8000.`,
        intent: 'error',
        emergencyLevel: 0,
        sources: [],
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId]);

  const newChat = useCallback(async () => {
    if (sessionId) {
      await clearSession(sessionId).catch(() => {});
    }
    setSessionId(null);
    setMessages([{
      id: 'welcome-new',
      role: 'assistant',
      content: "Starting a new conversation! How can I help you today?",
      intent: 'greeting',
      emergencyLevel: 0,
      emergencyMessage: null,
      sources: [],
    }]);
  }, [sessionId]);

  const pingHealth = useCallback(async () => {
    const status = await checkHealth();
    setHealthStatus(status);
    return status;
  }, []);

  return {
    messages,
    isLoading,
    sessionId,
    healthStatus,
    messagesEndRef,
    send,
    newChat,
    pingHealth,
  };
}