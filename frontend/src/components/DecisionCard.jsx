import React from 'react';
import './DecisionCard.css';

export default function DecisionCard({
  action = "ESCALATE",
  reason = "Historical responses indicate that this issue requires direct support follow-up.",
  onToggleAction
}) {
  const isEscalate = action === "ESCALATE";

  return (
    <div className={`card decision-card ${isEscalate ? 'state-escalate' : 'state-auto-handle'}`}>
      <div className="card-header decision-header">
        <div className="card-header-left">
          <div className="decision-icon-container">
            {isEscalate ? (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            ) : (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            )}
          </div>
          <div>
            <span className="decision-kicker">Routing Pipeline Decision</span>
            <div className="decision-badge-row">
              <span className={`decision-badge ${isEscalate ? 'badge-escalate' : 'badge-auto'}`}>
                {action}
              </span>
              <span className="decision-subtext">
                {isEscalate ? 'Manual Agent Review Required' : 'Ready for Automated Resolution'}
              </span>
            </div>
          </div>
        </div>

        <div className="toggle-visual-state">
          <span className="toggle-label">Test Visual State:</span>
          <button
            type="button"
            className={`toggle-btn ${!isEscalate ? 'active' : ''}`}
            onClick={() => onToggleAction("AUTO_HANDLE")}
          >
            AUTO-HANDLE
          </button>
          <button
            type="button"
            className={`toggle-btn ${isEscalate ? 'active' : ''}`}
            onClick={() => onToggleAction("ESCALATE")}
          >
            ESCALATE
          </button>
        </div>
      </div>

      <div className="card-body decision-body">
        <div className="reason-label">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          <span>Decision Reason & Rationale</span>
        </div>
        <p className="reason-text">
          {reason}
        </p>

        <div className="decision-rules-summary">
          <div className="rule-item">
            <span className="rule-bullet">•</span>
            <span>Escalates if historical resolution requests direct customer DM / external account lookup.</span>
          </div>
          <div className="rule-item">
            <span className="rule-bullet">•</span>
            <span>Escalates if historical similarity &lt; 0.20 threshold.</span>
          </div>
          <div className="rule-item">
            <span className="rule-bullet">•</span>
            <span>Auto-handles when confidence and historical similarity meet safe resolution standards.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
