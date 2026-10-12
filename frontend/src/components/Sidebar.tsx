import React from 'react';
import { Session } from '../types';
import { Plus, Trash2, MessageSquare } from 'lucide-react';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-header">
          <div className="brand-mark">L</div>
          <div className="brand-title">Lenny Growth AI</div>
        </div>
        <button className="new-chat-btn" onClick={onNewSession} title="Start a new chat">
          <Plus size={14} /> New chat
        </button>
      </div>

      <div className="session-list">
        <div className="session-list-heading">
          Chats ({sessions.length})
        </div>
        {sessions.length === 0 ? (
          <div className="empty-sessions-notice">
            No conversations yet
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = s.id === activeSessionId;
            return (
              <div
                key={s.id}
                className={`session-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectSession(s.id)}
              >
                <div className="session-item-content">
                  <MessageSquare size={13} className="session-icon" />
                  <span className="session-item-title">
                    {s.title}
                  </span>
                </div>
                <button
                  className="delete-btn"
                  title="Delete chat"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.id);
                  }}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
};
