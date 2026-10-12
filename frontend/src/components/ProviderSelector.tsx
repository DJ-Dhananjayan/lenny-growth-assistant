import React from 'react';
import { ProviderOption } from '../types';

interface ProviderSelectorProps {
  providers: ProviderOption[];
  activeProviderId: string;
  onSelectProvider: (providerId: string) => void;
}

export const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  providers,
  activeProviderId,
  onSelectProvider,
}) => {
  const current = providers.find((p) => p.id === activeProviderId) || providers[0];

  return (
    <div className="provider-selector-wrap">
      <div className="provider-status-indicator">
        <span
          className={`status-dot ${current?.available ? 'online' : 'offline'}`}
          title={current?.available ? 'Provider connected' : (current?.error_message || 'Offline')}
        />
      </div>
      <select
        value={activeProviderId}
        onChange={(e) => onSelectProvider(e.target.value)}
        className="provider-select"
      >
        {providers.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name} {p.available ? '' : '(Offline)'}
          </option>
        ))}
      </select>
    </div>
  );
};
