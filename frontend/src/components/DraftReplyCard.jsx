import React, { useState } from 'react';
import './DraftReplyCard.css';

export default function DraftReplyCard({
  draftReply,
  setDraftReply
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!draftReply) return;
    navigator.clipboard.writeText(draftReply);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card draft-reply-card">
      <div className="card-header">
        <div className="card-header-left">
          <div className="card-icon-badge draft-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          </div>
          <div>
            <h2 className="card-title">Grounded Draft Reply</h2>
            <p className="card-description">Context-aware customer response synthesized from retrieved resolution context.</p>
          </div>
        </div>

        <div className="draft-actions">
          <button
            type="button"
            className="action-btn"
            onClick={handleCopy}
            title="Copy draft reply to clipboard"
          >
            {copied ? (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span style={{ color: '#10b981' }}>Copied!</span>
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
                <span>Copy Reply</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="card-body">
        <textarea
          className="reply-textarea"
          rows={6}
          value={draftReply}
          onChange={(e) => setDraftReply(e.target.value)}
          placeholder="AI-generated draft reply will appear here..."
        />
      </div>

      <div className="card-footer">
        <div className="draft-tips">
          <span>Editable by support agent before dispatching.</span>
        </div>
        <div className="dispatch-actions">
          <button type="button" className="btn-secondary" onClick={() => alert("Draft saved as internal note (UI skeleton).")}>
            Save as Internal Note
          </button>
          <button type="button" className="btn-primary" onClick={() => alert("Dispatching response to customer (UI skeleton).")}>
            Send Response
          </button>
        </div>
      </div>
    </div>
  );
}
