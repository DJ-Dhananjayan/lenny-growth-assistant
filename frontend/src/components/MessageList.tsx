import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message, Artifact } from '../types';
import { CitationsList } from './CitationsList';
import { FileText, Loader2 } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onOpenArtifact: (art: Artifact) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  onOpenArtifact,
}) => {
  if (!messages || messages.length === 0) {
    return (
      <div className="empty-chat-state">
        <div className="empty-chat-title">The Lenny Growth Assistant</div>
        <div className="empty-chat-subtitle">
          Evidence-grounded strategy insights from Lenny's Podcast transcripts. Ask about product frameworks, founder-led mode, growth loops, or generate publication-ready essays.
        </div>
      </div>
    );
  }

  return (
    <div className="messages-container">
      {messages.map((msg) => {
        const isUser = msg.role === 'user';
        const citations = msg.citations || msg.citations_json || [];
        const artifact = msg.artifact || msg.artifact_json;

        return (
          <div key={msg.id} className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}>
            <div className={`message-content ${isUser ? 'user-message' : 'assistant-message'}`}>
              <div className="message-author">
                {isUser ? 'You' : 'Lenny Assistant'}
              </div>

              {isUser ? (
                <div className="user-text">{msg.content}</div>
              ) : (
                <div className="assistant-body">
                  <div className="markdown-preview">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>

                  {/* Clean Citations List */}
                  {citations && citations.length > 0 && (
                    <CitationsList citations={citations} />
                  )}

                  {/* Subdued Artifact Button */}
                  {artifact && (
                    <div className="artifact-trigger-wrap">
                      <button
                        onClick={() => onOpenArtifact(artifact)}
                        className="artifact-trigger-btn"
                      >
                        <FileText size={14} />
                        <span>Artifact: {artifact.title}</span>
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {isLoading && (
        <div className="message-row assistant-row">
          <div className="message-content assistant-message loading-state">
            <Loader2 size={15} className="spinner-icon" />
            <span>Thinking...</span>
          </div>
        </div>
      )}
    </div>
  );
};
