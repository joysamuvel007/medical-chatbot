

import React from 'react';

const EMERGENCY_STYLES = {
  4: { bg: 'bg-red-100', border: 'border-red-500', text: 'text-red-800', label: '🚨 CRITICAL EMERGENCY' },
  3: { bg: 'bg-orange-100', border: 'border-orange-500', text: 'text-orange-800', label: '⚠️ URGENT' },
  2: { bg: 'bg-yellow-100', border: 'border-yellow-400', text: 'text-yellow-800', label: '⚠️ See a Doctor Soon' },
  1: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-800', label: 'ℹ️ Mild Concern' },
};

const INTENT_BADGES = {
  symptom_check:    { label: 'Symptoms', color: 'bg-orange-100 text-orange-700' },
  medication_info:  { label: 'Medication', color: 'bg-purple-100 text-purple-700' },
  appointment:      { label: 'Appointment', color: 'bg-blue-100 text-blue-700' },
  wellness_advice:  { label: 'Wellness', color: 'bg-green-100 text-green-700' },
  mental_health:    { label: 'Mental Health', color: 'bg-pink-100 text-pink-700' },
  emergency:        { label: 'Emergency', color: 'bg-red-100 text-red-700' },
  general_medical:  { label: 'Medical Info', color: 'bg-teal-100 text-teal-700' },
  greeting:         { label: 'Greeting', color: 'bg-gray-100 text-gray-600' },
  farewell:         { label: 'Farewell', color: 'bg-gray-100 text-gray-600' },
  out_of_scope:     { label: 'Off-topic', color: 'bg-gray-100 text-gray-600' },
};

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const emergency = EMERGENCY_STYLES[message.emergencyLevel];
  const intentBadge = message.intent ? INTENT_BADGES[message.intent] : null;

  return (
    <div className={`message-enter flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>

        {/* Emergency Banner (above the message bubble) */}
        {!isUser && emergency && message.emergencyLevel >= 2 && (
          <div className={`mb-2 px-3 py-2 rounded-lg border ${emergency.bg} ${emergency.border} ${emergency.text} text-sm font-semibold`}>
            {emergency.label}
            {message.emergencyMessage && (
              <p className="font-normal mt-1">{message.emergencyMessage}</p>
            )}
          </div>
        )}

        {/* Message Bubble */}
        <div className={`px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : 'bg-white text-gray-800 rounded-tl-sm shadow-sm border border-gray-100'
        }`}>
          {/* Bot avatar label */}
          {!isUser && (
            <div className="text-xs text-gray-400 mb-1 font-medium">Healthcare Assistant</div>
          )}

          {/* Message text — preserve newlines */}
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {/* Intent badge + confidence (bot messages only) */}
          {!isUser && intentBadge && message.intent !== 'greeting' && (
            <div className="mt-2 flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${intentBadge.color}`}>
                {intentBadge.label}
              </span>
              {message.confidence !== undefined && (
                <span className="text-xs text-gray-400">
                  {Math.round(message.confidence * 100)}% confidence
                </span>
              )}
            </div>
          )}
        </div>

        {/* Sources section */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 px-3 py-2 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-xs font-semibold text-gray-500 mb-1">📚 Sources</p>
            <ul className="space-y-1">
              {message.sources.map((source, i) => (
                <li key={i} className="text-xs">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline font-medium"
                  >
                    {source.title}
                  </a>
                  {source.is_trusted && (
                    <span className="ml-1 text-green-600">✓</span>
                  )}
                  {source.snippet && (
                    <p className="text-gray-500 mt-0.5">{source.snippet.substring(0, 100)}...</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}