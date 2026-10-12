import React, { useState, KeyboardEvent } from 'react';
import { ArrowUp } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (text: string) => void;
  disabled: boolean;
  hasMessages?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled,
  hasMessages = false,
}) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSendMessage(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestions = [
    'What is the LNO Framework by Shreyas Doshi?',
    'How does Brian Chesky explain Founder-Led Mode at Airbnb?',
    'Write a Ship 30 for 30 essay on Product-Led Growth loops',
  ];

  return (
    <div className="input-container">
      {/* Show compact suggestions only near empty state */}
      {!hasMessages && (
        <div className="suggestion-strip">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              className="suggestion-chip"
              onClick={() => onSendMessage(s)}
              disabled={disabled}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="input-box">
        <textarea
          className="chat-textarea"
          placeholder="Ask a product or growth strategy question..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          title="Send message (Enter)"
        >
          <ArrowUp size={16} />
        </button>
      </div>
    </div>
  );
};
