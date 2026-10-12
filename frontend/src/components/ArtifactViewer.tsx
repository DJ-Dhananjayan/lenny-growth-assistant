import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Artifact } from '../types';
import { SandboxedFrame } from './SandboxedFrame';
import { X, Copy, Download, Check, Eye, Code } from 'lucide-react';

interface ArtifactViewerProps {
  artifact: Artifact;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'source'>('preview');
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(artifact.content);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = artifact.content;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback copy failed gracefully
    }
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === 'html' ? 'html' : 'md';
    const mime = artifact.artifact_type === 'html' ? 'text/html' : 'text/markdown';
    const blob = new Blob([artifact.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artifact-panel">
      <div className="artifact-header">
        <div className="artifact-title" title={artifact.title}>
          {artifact.title}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="artifact-tabs">
            <button
              className={`tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              <Eye size={12} style={{ display: 'inline', marginRight: '3px' }} /> Preview
            </button>
            <button
              className={`tab-btn ${activeTab === 'source' ? 'active' : ''}`}
              onClick={() => setActiveTab('source')}
            >
              <Code size={12} style={{ display: 'inline', marginRight: '3px' }} /> Source
            </button>
          </div>
          <button
            onClick={handleCopy}
            title="Copy Content"
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
          </button>
          <button
            onClick={handleDownload}
            title="Download File"
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <Download size={16} />
          </button>
          <button
            onClick={onClose}
            title="Close Panel"
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <X size={18} />
          </button>
        </div>
      </div>

      <div className="artifact-body">
        {activeTab === 'source' ? (
          <pre className="source-code">{artifact.content}</pre>
        ) : artifact.artifact_type === 'html' ? (
          <SandboxedFrame htmlContent={artifact.content} title={artifact.title} />
        ) : (
          <div className="markdown-preview">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};
