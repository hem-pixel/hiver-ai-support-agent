import React from 'react';
import './CustomerMessageCard.css';

export default function CustomerMessageCard({
  message,
  setMessage,
  onAnalyze,
  isAnalyzing,
  onLoadSample,
  error
}) {
  return (
    <div className="card customer-message-card">
      <div className="card-header">
        <div className="card-header-left">
          <div className="card-icon-badge">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
            </svg>
          </div>
          <div>
            <h2 className="card-title">Customer Inbound Message</h2>
            <p className="card-description">Enter an incoming customer inquiry to run through the AI pipeline.</p>
          </div>
        </div>

        <div className="sample-chips">
          <span className="sample-label">Quick scenarios:</span>
          <button
            type="button"
            className="chip-btn"
            onClick={() => onLoadSample("I was charged too much for my Uber ride and want a refund")}
            disabled={isAnalyzing}
          >
            Fare Overcharge
          </button>
          <button
            type="button"
            className="chip-btn"
            onClick={() => onLoadSample("I cannot login to my Uber account")}
            disabled={isAnalyzing}
          >
            Account Login
          </button>
          <button
            type="button"
            className="chip-btn"
            onClick={() => onLoadSample("My Uber driver was rude")}
            disabled={isAnalyzing}
          >
            Driver Conduct
          </button>
          <button
            type="button"
            className="chip-btn"
            onClick={() => onLoadSample("Uber Eats delivery is late")}
            disabled={isAnalyzing}
          >
            Eats Delivery
          </button>
        </div>
      </div>

      <div className="card-body">
        <textarea
          className="message-textarea"
          rows={5}
          placeholder="Paste a customer support message here..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isAnalyzing}
        />

        {error && (
          <div className="input-error-banner" role="alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{error}</span>
          </div>
        )}
      </div>

      <div className="card-footer">
        <div className="char-count">
          {message.length} characters
        </div>
        <button
          type="button"
          className="btn-primary analyze-btn"
          onClick={onAnalyze}
          disabled={isAnalyzing || !message.trim()}
        >
          {isAnalyzing ? (
            <>
              <span className="spinner"></span>
              <span>Analyzing Message...</span>
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              <span>Analyze Customer Message</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
