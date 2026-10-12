import React from 'react';
import { Session, Message, ProviderOption, Artifact } from '../types';
import { ProviderSelector } from './ProviderSelector';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface ChatPanelProps {
  activeSession: Session | null;
  messages: Message[];
  isLoading: boolean;
  providers: ProviderOption[];
  activeProviderId: string;
  onSelectProvider: (id: string) => void;
  onSendMessage: (text: string) => void;
  onOpenArtifact: (art: Artifact) => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  activeSession,
  messages,
  isLoading,
  providers,
  activeProviderId,
  onSelectProvider,
  onSendMessage,
  onOpenArtifact,
}) => {
  return (
    <main className="chat-workspace">
      <header className="chat-header">
        <div className="chat-header-title">
          {activeSession ? activeSession.title : 'The Lenny Growth Assistant'}
        </div>
        <ProviderSelector
          providers={providers}
          activeProviderId={activeProviderId}
          onSelectProvider={onSelectProvider}
        />
      </header>

      <MessageList
        messages={messages}
        isLoading={isLoading}
        onOpenArtifact={onOpenArtifact}
      />

      <MessageInput
        onSendMessage={onSendMessage}
        disabled={isLoading}
        hasMessages={messages.length > 0}
      />
    </main>
  );
};
