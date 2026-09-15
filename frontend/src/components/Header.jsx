import React from 'react';
import './Header.css';

export default function Header({ isConnected = true }) {
  return (
    <header className="top-header">
      <div className="header-left">
        <h1 className="header-title">AI Support Agent</h1>
        <p className="header-subtitle">
          Assists support teams by classifying inbound customer intents, retrieving grounded historical resolutions, drafting contextual replies, and routing decisions to auto-handle or escalate.
        </p>
      </div>
      <div className="header-right">
        <div className={`preview-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          <span className={`pulse-indicator ${isConnected ? 'online' : 'offline'}`}></span>
          <span>{isConnected ? 'API Connected (Port 8000)' : 'API Disconnected'}</span>
        </div>
      </div>
    </header>
  );
}
