import React, { useState, useEffect } from 'react';
import { api } from './api/client';
import { Session, Message, ProviderOption, Artifact } from './types';
import { Sidebar } from './components/Sidebar';
import { ChatPanel } from './components/ChatPanel';
import { ArtifactViewer } from './components/ArtifactViewer';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [providers, setProviders] = useState<ProviderOption[]>([]);
  const [activeProviderId, setActiveProviderId] = useState<string>('ollama');
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load provider configurations and sessions on mount
  useEffect(() => {
    const initApp = async () => {
      try {
        const provRes = await api.listProviders();
        setProviders(provRes.providers);
        setActiveProviderId(provRes.active_provider);

        const sessionList = await api.listSessions();
        setSessions(sessionList);
        if (sessionList.length > 0) {
          setActiveSessionId(sessionList[0].id);
        }
      } catch (err: any) {
        console.error('App init error:', err);
        setErrorMsg(`Failed to connect to backend API: ${err.message}`);
      }
    };
    initApp();
  }, []);

  // Load message history when active session changes
  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }
    const loadSessionMessages = async () => {
      try {
        const sessionDetail = await api.getSession(activeSessionId);
        const sorted = (sessionDetail.messages || []).slice().sort(
          (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
        setMessages(sorted);
      } catch (err: any) {
        console.error('Session load error:', err);
      }
    };
    loadSessionMessages();
  }, [activeSessionId]);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
    setErrorMsg(null);
  };

  const handleNewSession = async () => {
    try {
      const newSession = await api.createSession('New Growth Chat', activeProviderId);
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      setMessages([]);
      setActiveArtifact(null);
      setErrorMsg(null);
    } catch (err: any) {
      setErrorMsg(`Failed to create new session: ${err.message}`);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await api.deleteSession(id);
      const updated = sessions.filter((s) => s.id !== id);
      setSessions(updated);
      if (activeSessionId === id) {
        setActiveSessionId(updated.length > 0 ? updated[0].id : null);
        setMessages([]);
        setActiveArtifact(null);
      }
    } catch (err: any) {
      setErrorMsg(`Failed to delete session: ${err.message}`);
    }
  };

  const handleSelectProvider = async (providerId: string) => {
    try {
      setActiveProviderId(providerId);
      await api.selectProvider(providerId);
    } catch (err: any) {
      setErrorMsg(`Provider switch failed: ${err.message}`);
    }
  };

  const handleSendMessage = async (text: string) => {
    let currentSessionId = activeSessionId;
    if (!currentSessionId) {
      try {
        const created = await api.createSession(text.slice(0, 35) + '...', activeProviderId);
        setSessions((prev) => [created, ...prev]);
        currentSessionId = created.id;
        setActiveSessionId(created.id);
      } catch (err: any) {
        setErrorMsg(`Failed to create session: ${err.message}`);
        return;
      }
    }

    // Optimistic user message append
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentSessionId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const assistantMsg = await api.sendMessage(currentSessionId, text, activeProviderId);
      // Fresh session fetch ensures 100% database order and true IDs
      const sessionDetail = await api.getSession(currentSessionId);
      const sorted = (sessionDetail.messages || []).slice().sort(
        (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setMessages(sorted);
      
      // Auto-open artifact if generated
      const generatedArtifact = assistantMsg.artifact || assistantMsg.artifact_json;
      if (generatedArtifact) {
        setActiveArtifact(generatedArtifact);
      }

      // Update session title in list
      setSessions((prev) =>
        prev.map((s) => (s.id === currentSessionId ? { ...s, title: text.slice(0, 35) + '...' } : s))
      );
    } catch (err: any) {
      setErrorMsg(`Inference failure: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const activeSession = sessions.find((s) => s.id === activeSessionId) || null;

  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
      />

      <div style={{ flex: 1, display: 'flex', position: 'relative' }}>
        <ChatPanel
          activeSession={activeSession}
          messages={messages}
          isLoading={isLoading}
          providers={providers}
          activeProviderId={activeProviderId}
          onSelectProvider={handleSelectProvider}
          onSendMessage={handleSendMessage}
          onOpenArtifact={(art) => setActiveArtifact(art)}
        />

        {errorMsg && (
          <div
            style={{
              position: 'absolute',
              top: '70px',
              left: '20px',
              right: '20px',
              backgroundColor: 'rgba(239, 68, 68, 0.95)',
              color: '#fff',
              padding: '12px 16px',
              borderRadius: '8px',
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              zIndex: 10,
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            }}
          >
            <span>⚠️ {errorMsg}</span>
            <button
              onClick={() => setErrorMsg(null)}
              style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}
            >
              ✕
            </button>
          </div>
        )}

        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        )}
      </div>
    </div>
  );
};

export default App;
