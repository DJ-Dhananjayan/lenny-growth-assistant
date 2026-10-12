import React from 'react';

interface SandboxedFrameProps {
  htmlContent: string;
  title?: string;
}

export const SandboxedFrame: React.FC<SandboxedFrameProps> = ({ htmlContent, title = 'HTML Artifact' }) => {
  // Construct sanitized HTML payload with strict CSP meta header
  const srcDocPayload = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: https:;">
      <style>
        body {
          font-family: system-ui, -apple-system, sans-serif;
          background-color: #ffffff;
          color: #1a202c;
          padding: 16px;
          margin: 0;
          line-height: 1.5;
        }
      </style>
    </head>
    <body>
      ${htmlContent}
    </body>
    </html>
  `;

  return (
    <iframe
      title={title}
      srcDoc={srcDocPayload}
      sandbox=""
      style={{
        width: '100%',
        height: '100%',
        minHeight: '400px',
        border: '1px solid #2d3748',
        borderRadius: '8px',
        backgroundColor: '#ffffff',
      }}
    />
  );
};
