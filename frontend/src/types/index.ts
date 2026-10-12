export interface Citation {
  episode_title: string;
  guest: string;
  episode_url?: string;
  chunk_id: string;
  snippet: string;
  score?: number;
}

export interface Artifact {
  title: string;
  artifact_type: 'markdown' | 'html';
  content: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  citations_json?: Citation[];
  artifact?: Artifact;
  artifact_json?: Artifact;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  provider: string;
  model: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ProviderOption {
  id: string;
  name: string;
  type: 'local' | 'cloud';
  available: boolean;
  models: string[];
  default_model: string;
  description: string;
  error_message?: string;
}

export interface ProviderConfigResponse {
  active_provider: string;
  providers: ProviderOption[];
}
