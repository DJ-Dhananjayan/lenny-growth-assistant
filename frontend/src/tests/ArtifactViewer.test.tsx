import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ArtifactViewer } from '../components/ArtifactViewer';
import { Artifact } from '../types';

describe('ArtifactViewer Component & Sandboxing', () => {
  const markdownArtifact: Artifact = {
    title: 'Ship 30 Essay: PLG Loops',
    artifact_type: 'markdown',
    content: '### The Power of PLG Loops\n\n* Loops compound.\n* Retention drives acquisition.',
  };

  const htmlArtifact: Artifact = {
    title: 'Interactive PLG Metrics Card',
    artifact_type: 'html',
    content: '<div class="card"><h2>PLG Metrics</h2><p>Retention: 85%</p></div>',
  };

  it('renders markdown artifact preview correctly', () => {
    const handleClose = vi.fn();
    render(<ArtifactViewer artifact={markdownArtifact} onClose={handleClose} />);

    expect(screen.getByText(/Ship 30 Essay: PLG Loops/i)).toBeInTheDocument();
    expect(screen.getByText(/The Power of PLG Loops/i)).toBeInTheDocument();
    expect(screen.getByText(/Loops compound/i)).toBeInTheDocument();
  });

  it('renders HTML artifact inside strictly sandboxed iframe', () => {
    const handleClose = vi.fn();
    const { container } = render(<ArtifactViewer artifact={htmlArtifact} onClose={handleClose} />);

    const iframe = container.querySelector('iframe');
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('sandbox', '');
    expect(iframe?.getAttribute('sandbox')).not.toContain('allow-scripts');
    expect(iframe?.getAttribute('sandbox')).not.toContain('allow-same-origin');

    const srcDoc = iframe?.getAttribute('srcdoc') || '';
    expect(srcDoc).toContain("Content-Security-Policy");
    expect(srcDoc).toContain("default-src 'none'");
    expect(srcDoc).toContain(htmlArtifact.content);
  });

  it('toggles between preview and raw source code tabs', () => {
    const handleClose = vi.fn();
    render(<ArtifactViewer artifact={markdownArtifact} onClose={handleClose} />);

    const sourceBtn = screen.getByRole('button', { name: /Source/i });
    fireEvent.click(sourceBtn);

    const preTag = document.querySelector('pre.source-code');
    expect(preTag).toBeInTheDocument();
    expect(preTag?.textContent).toContain('### The Power of PLG Loops');

    const previewBtn = screen.getByRole('button', { name: /Preview/i });
    fireEvent.click(previewBtn);
    expect(screen.getByText(/The Power of PLG Loops/i)).toBeInTheDocument();
  });

  it('triggers onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(<ArtifactViewer artifact={markdownArtifact} onClose={handleClose} />);

    const closeBtn = screen.getByTitle('Close Panel');
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
