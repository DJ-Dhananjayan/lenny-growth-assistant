import { Session, Message, ProviderConfigResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = 'An error occurred';
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errData.message || response.statusText;
    } catch {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  async getHealth() {
    return fetchJson<{ status: string; database: string; active_provider: string }>('/health');
  },

  async listSessions(): Promise<Session[]> {
    return fetchJson<Session[]>('/sessions');
  },

  async createSession(title?: string, provider?: string): Promise<Session> {
    return fetchJson<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify({ title: title || 'New Growth Chat', provider }),
    });
  },

  async getSession(id: string): Promise<Session> {
    return fetchJson<Session>(`/sessions/${id}`);
  },

  async deleteSession(id: string): Promise<void> {
    await fetch(`${API_BASE_URL}/sessions/${id}`, { method: 'DELETE' });
  },

  async sendMessage(sessionId: string, content: string, provider?: string, model?: string): Promise<Message> {
    return fetchJson<Message>(`/chat/${sessionId}`, {
      method: 'POST',
      body: JSON.stringify({ content, provider, model }),
    });
  },

  async listProviders(): Promise<ProviderConfigResponse> {
    return fetchJson<ProviderConfigResponse>('/providers');
  },

  async selectProvider(providerId: string): Promise<{ success: boolean; active_provider: string }> {
    return fetchJson('/providers/select', {
      method: 'POST',
      body: JSON.stringify({ provider_id: providerId }),
    });
  },
};
