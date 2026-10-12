import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import App from '../App';

describe('Lenny Growth Assistant UI', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    (global.fetch as any).mockImplementation((url: string) => {
      if (url.includes('/providers')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              active_provider: 'ollama',
              providers: [
                {
                  id: 'ollama',
                  name: 'Ollama (Local)',
                  type: 'local',
                  available: true,
                  models: ['llama3.2'],
                  default_model: 'llama3.2',
                  description: 'Ollama',
                },
              ],
            }),
        });
      }
      if (url.includes('/sessions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    });
  });

  it('renders application brand title and provider selector', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Lenny Growth AI/i)).toBeInTheDocument();
      expect(screen.getByText(/Ollama \(Local\)/i)).toBeInTheDocument();
    });
  });
});
