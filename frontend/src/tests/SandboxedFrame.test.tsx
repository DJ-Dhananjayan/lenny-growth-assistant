import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SandboxedFrame } from '../components/SandboxedFrame';

describe('SandboxedFrame Component Security', () => {
  it('renders an iframe with empty sandbox attribute and no script/same-origin permissions', () => {
    const maliciousHtml = '<script>alert("xss")</script><div id="test-card">Growth Card</div>';
    const { container } = render(
      <SandboxedFrame htmlContent={maliciousHtml} title="Test Card" />
    );

    const iframe = container.querySelector('iframe');
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('title', 'Test Card');

    // Strict sandbox verification: attribute must exist and MUST NOT contain allow-scripts or allow-same-origin
    const sandboxAttr = iframe?.getAttribute('sandbox');
    expect(sandboxAttr).toBe('');
    expect(sandboxAttr).not.toContain('allow-scripts');
    expect(sandboxAttr).not.toContain('allow-same-origin');

    // Verify CSP meta header in srcDoc
    const srcDoc = iframe?.getAttribute('srcdoc') || '';
    expect(srcDoc).toContain("Content-Security-Policy");
    expect(srcDoc).toContain("default-src 'none'");
    expect(srcDoc).toContain(maliciousHtml);
  });
});
