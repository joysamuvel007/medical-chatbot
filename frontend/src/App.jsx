
import { useState, useEffect, useRef } from 'react';
import { useChat } from './hooks/useChat';
import ChatMessage from './components/ChatMessage';
import TypingIndicator from './components/TypingIndicator';
import StatusBar from './components/StatusBar';

const SUGGESTED_QUESTIONS = [
  "I have a headache and mild fever",
  "What are common cold symptoms?",
  "How much water should I drink daily?",
  "Tips to reduce stress and anxiety",
  "What does ibuprofen treat?",
  "How can I improve my sleep?",
];

export default function App() {
  const { messages, isLoading, sessionId, healthStatus, messagesEndRef, send, newChat, pingHealth } = useChat();
  const [input, setInput] = useState('');
  const inputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    pingHealth();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!input.trim()) return;
    send(input.trim());
    setInput('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (question) => {
    send(question);
    inputRef.current?.focus();
  };

  return (
    <div className="flex h-screen bg-gray-50 font-sans">

      {/* ── LEFT SIDEBAR ────────────────────────────── */}
      <aside className="w-72 bg-white border-r border-gray-200 flex flex-col p-4 gap-4 hidden md:flex">

        {/* Logo / Title */}
        <div className="flex items-center gap-3 pb-3 border-b border-gray-100">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white text-lg">
            🏥
          </div>
          <div>
            <h1 className="font-bold text-gray-800 text-sm">Healthcare Assistant</h1>
            <p className="text-xs text-gray-400">Powered by Ollama (local AI)</p>
          </div>
        </div>

        {/* AI Status */}
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">AI Status</p>
          <StatusBar healthStatus={healthStatus} onCheck={pingHealth} />
        </div>

        {/* New Chat Button */}
        <button
          onClick={newChat}
          className="w-full py-2 px-3 bg-blue-50 hover:bg-blue-100 text-blue-700 text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <span>✚</span> New Conversation
        </button>

        {/* Suggested Questions */}
        <div className="flex-1 overflow-y-auto">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Try Asking</p>
          <div className="space-y-1.5">
            {SUGGESTED_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSuggestion(q)}
                disabled={isLoading}
                className="w-full text-left text-xs text-gray-600 hover:text-blue-700 hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Session info */}
        {sessionId && (
          <div className="pt-2 border-t border-gray-100">
            <p className="text-xs text-gray-400">
              Session: <span className="font-mono">{sessionId}</span>
            </p>
          </div>
        )}

        {/* Disclaimer */}
        <div className="text-xs text-gray-400 leading-relaxed border-t border-gray-100 pt-3">
          ⚠️ For informational purposes only. Not a substitute for professional medical advice.
        </div>
      </aside>

      {/* ── MAIN CHAT AREA ──────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0">

        {/* Top bar (mobile only) */}
        <div className="md:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <h1 className="font-bold text-gray-800">🏥 Healthcare Assistant</h1>
          <button onClick={newChat} className="text-sm text-blue-600 font-medium">
            New Chat
          </button>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto chat-scroll px-4 py-4 md:px-8">
          <div className="max-w-3xl mx-auto">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Input area */}
        <div className="bg-white border-t border-gray-200 px-4 py-4 md:px-8">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-end gap-3 bg-gray-50 rounded-2xl border border-gray-200 px-4 py-3 focus-within:border-blue-400 focus-within:ring-1 focus-within:ring-blue-400 transition-all">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe your symptoms or ask a health question..."
                rows={1}
                disabled={isLoading}
                className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 resize-none outline-none max-h-32 disabled:opacity-50"
                style={{ minHeight: '24px' }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="w-9 h-9 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-xl flex items-center justify-center transition-colors flex-shrink-0"
                title="Send message"
              >
                {isLoading ? (
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="32" strokeDashoffset="10" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1.5 ml-1">
              Press Enter to send • Shift+Enter for new line
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}