import React from 'react';
import './Header.css';

export default function Header() {
  return (
    <header className="top-header">
      <div className="header-left">
        <h1 className="header-title">AI Support Agent</h1>
        <p className="header-subtitle">
          Assists support teams by classifying inbound customer intents, retrieving grounded historical resolutions, drafting contextual replies, and routing decisions to auto-handle or escalate.
        </p>
      </div>
      <div className="header-right">
        <div className="preview-indicator">
          <span className="pulse-indicator"></span>
          <span>UI Skeleton Mode</span>
        </div>
      </div>
    </header>
  );
}
