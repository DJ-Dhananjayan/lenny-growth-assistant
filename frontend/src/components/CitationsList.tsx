import React, { useState } from 'react';
import { Citation } from '../types';
import { ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

interface CitationsListProps {
  citations: Citation[];
}

export const CitationsList: React.FC<CitationsListProps> = ({ citations }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="citations-block">
      <div className="citations-header">
        Sources ({citations.length})
      </div>
      <div className="citations-list">
        {citations.map((c) => {
          const isExpanded = expandedId === c.chunk_id;
          return (
            <div key={c.chunk_id} className="citation-item">
              <div className="citation-row">
                <div className="citation-meta">
                  <span className="citation-guest">{c.guest}</span>
                  <span className="citation-sep">·</span>
                  <span className="citation-title">{c.episode_title}</span>
                </div>
                <div className="citation-actions">
                  {c.episode_url && (
                    <a
                      href={c.episode_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="citation-link"
                      title="Open podcast episode"
                    >
                      Listen <ExternalLink size={11} />
                    </a>
                  )}
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : c.chunk_id)}
                    className="citation-expand-btn"
                    title={isExpanded ? 'Hide excerpt' : 'View excerpt'}
                  >
                    {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  </button>
                </div>
              </div>
              {isExpanded && (
                <div className="citation-excerpt">
                  "{c.snippet}"
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
