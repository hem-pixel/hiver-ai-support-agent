import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CustomerMessageCard from './components/CustomerMessageCard';
import AnalysisCards from './components/AnalysisCards';
import HistoricalResolutionCard from './components/HistoricalResolutionCard';
import DraftReplyCard from './components/DraftReplyCard';
import DecisionCard from './components/DecisionCard';
import { analyzeMessage, checkHealth } from './services/api';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [message, setMessage] = useState('');
  const [intent, setIntent] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [similarity, setSimilarity] = useState(null);
  const [historicalMatch, setHistoricalMatch] = useState(null);
  const [draftReply, setDraftReply] = useState('');
  const [action, setAction] = useState(null);
  const [reason, setReason] = useState(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  // Check backend health on initial load and keep monitoring for auto-reconnect
  useEffect(() => {
    let isMounted = true;
    let consecutiveFailures = 0;

    const verifyHealth = async () => {
      try {
        await checkHealth();
        if (isMounted) {
          consecutiveFailures = 0;
          setIsConnected(true);
          // If a previous error was a backend disconnection banner, clear it automatically
          setError((prev) => (prev && prev.includes('FastAPI backend is offline') ? null : prev));
        }
      } catch {
        if (isMounted) {
          consecutiveFailures += 1;
          // Require at least 2 consecutive failures before switching badge to disconnected
          // This prevents transient Windows IPv6 SYN or GC pauses from causing spurious UI errors
          if (consecutiveFailures >= 2) {
            setIsConnected(false);
          }
        }
      }
    };

    // Immediate check on mount
    verifyHealth();

    // Auto-reconnect poll interval (checks every 3.5 seconds)
    const interval = setInterval(verifyHealth, 3500);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleRetryConnection = async () => {
    try {
      await checkHealth();
      setIsConnected(true);
      setError(null);
    } catch (err) {
      setIsConnected(false);
      setError(err.message);
    }
  };

  const handleLoadSample = (sampleText) => {
    setMessage(sampleText);
    setError(null);
  };

  const handleAnalyze = async () => {
    const trimmed = (message || '').trim();
    if (!trimmed) {
      setError('Please enter a customer message before analyzing.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await analyzeMessage(trimmed);

      // Populate dashboard with real backend data
      setIntent(response.intent || null);
      setConfidence(response.confidence ?? null);
      setSimilarity(typeof response.similarity === 'number' ? response.similarity : 0);
      setHistoricalMatch(response.historical_match || null);
      setDraftReply(response.draft_reply || '');
      setAction(response.decision || null);
      setReason(response.decision_reason || null);

      setHasAnalyzed(true);
      setIsConnected(true);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
      // Check if backend connection failed
      if (err.message.includes('unavailable') || err.message.includes('FastAPI')) {
        setIsConnected(false);
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const renderContent = () => {
    if (activeTab === 'evaluation') {
      return (
        <div className="tab-pane">
          <div className="card placeholder-panel">
            <h2 className="panel-title">Evaluation Benchmark Suite</h2>
            <p className="panel-desc">
              Ground-truth performance on the 200-sample human-verified golden dataset (50-sample stratified holdout).
            </p>
            <div className="eval-stats-grid">
              <div className="eval-stat-card">
                <span className="stat-label">Rule-Based Baseline</span>
                <span className="stat-value">64.00%</span>
                <span className="stat-meta">Macro F1: 0.59 • Weighted: 0.64</span>
              </div>
              <div className="eval-stat-card">
                <span className="stat-label">TF-IDF Baseline</span>
                <span className="stat-value">40.00%</span>
                <span className="stat-meta">Logistic Regression n-grams</span>
              </div>
              <div className="eval-stat-card">
                <span className="stat-label">Evaluation Corpus</span>
                <span className="stat-value">200 Samples</span>
                <span className="stat-meta">10 Target Support Intents</span>
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (activeTab === 'history') {
      return (
        <div className="tab-pane">
          <div className="card placeholder-panel">
            <h2 className="panel-title">Conversation History</h2>
            <p className="panel-desc">
              Audit log of processed customer inquiries, matched historical resolutions, and routing decisions.
            </p>
          </div>
        </div>
      );
    }

    if (activeTab === 'settings') {
      return (
        <div className="tab-pane">
          <div className="card placeholder-panel">
            <h2 className="panel-title">Agent Settings &amp; Thresholds</h2>
            <p className="panel-desc">
              Configurable routing rules: Similarity cutoff threshold (&gt;= 0.20), human escalation trigger phrases, and auto-dispatch policies.
            </p>
          </div>
        </div>
      );
    }

    // Default: Dashboard / New Conversation
    return (
      <div className="workspace-container">
        {/* 1. Customer Message Input Section */}
        <CustomerMessageCard
          message={message}
          setMessage={setMessage}
          onAnalyze={handleAnalyze}
          isAnalyzing={isAnalyzing}
          onLoadSample={handleLoadSample}
          error={error}
          onRetryConnection={handleRetryConnection}
          isConnected={isConnected}
        />

        {/* 2. AI Analysis Section (3 Cards) */}
        <AnalysisCards
          intent={intent}
          confidence={confidence}
          similarity={similarity}
          hasAnalyzed={hasAnalyzed}
        />

        {/* Two-Column Responsive Layout for Details */}
        <div className="workspace-two-col">
          <div className="workspace-col-main">
            {/* 3. Draft Reply Section */}
            <DraftReplyCard
              draftReply={draftReply}
              setDraftReply={setDraftReply}
              hasAnalyzed={hasAnalyzed}
            />

            {/* 4. Historical Resolution Section */}
            <HistoricalResolutionCard
              historicalMatch={historicalMatch}
              similarity={similarity}
              hasAnalyzed={hasAnalyzed}
            />
          </div>

          <div className="workspace-col-side">
            {/* 5. Decision Section (AUTO_HANDLE vs ESCALATE) */}
            <DecisionCard
              action={action}
              reason={reason}
              hasAnalyzed={hasAnalyzed}
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />
      <div className="app-main">
        <Header isConnected={isConnected} />
        <main className="content-area">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
