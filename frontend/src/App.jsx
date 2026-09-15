import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CustomerMessageCard from './components/CustomerMessageCard';
import AnalysisCards from './components/AnalysisCards';
import HistoricalResolutionCard from './components/HistoricalResolutionCard';
import DraftReplyCard from './components/DraftReplyCard';
import DecisionCard from './components/DecisionCard';
import './App.css';

const SAMPLE_SCENARIOS = {
  overcharge: {
    message: "I was charged twice for my ride yesterday and need a refund",
    intent: "fare_or_charge_issue",
    confidence: 0.94,
    similarity: 0.7533,
    historicalCustomer: "@115873 I got charged twice for one ride I'm trying to get a refund can you help me",
    historicalSupport: "@438093 We can take a look! Send us a note via https://t.co/zJ6aIZinzb so our team can get in touch.",
    draftReply: "Sorry about the issue you're experiencing. Please send us a DM with your details so our support team can review this and assist you further.",
    action: "ESCALATE",
    reason: "Historical responses indicate that this issue requires direct support follow-up."
  },
  eats: {
    message: "My Uber Eats order arrived with missing food and wrong items",
    intent: "uber_eats_issue",
    confidence: 0.91,
    similarity: 0.4931,
    historicalCustomer: "@Uber_Support My uber eats is missing half of the order. how do we get the rest of the order delivered ?",
    historicalSupport: "@705609 Here to help! Send us a note here; https://t.co/ZFaWy0Lkdu and our team will be able to help.",
    draftReply: "We are sorry for the trouble with your order. Please provide your order details so our team can help resolve this delivery issue.",
    action: "ESCALATE",
    reason: "Historical responses indicate that this issue requires direct support follow-up."
  },
  account: {
    message: "Where can I view my ride receipt and billing history in the app?",
    intent: "app_or_technical_issue",
    confidence: 0.88,
    similarity: 0.6210,
    historicalCustomer: "@Uber_Support where do I find the trip receipt for my tax billing?",
    historicalSupport: "You can find all official ride receipts by tapping 'Your Trips' > selecting the ride > 'Receipt' in the Uber app.",
    draftReply: "You can view and download all past ride receipts by navigating to 'Activity' > selecting the trip > 'View Receipt' directly in your Uber app.",
    action: "AUTO_HANDLE",
    reason: "A sufficiently similar historical resolution was found (similarity: 0.6210) with verified standard resolution steps."
  }
};

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [message, setMessage] = useState(SAMPLE_SCENARIOS.overcharge.message);
  const [intent, setIntent] = useState(SAMPLE_SCENARIOS.overcharge.intent);
  const [confidence, setConfidence] = useState(SAMPLE_SCENARIOS.overcharge.confidence);
  const [similarity, setSimilarity] = useState(SAMPLE_SCENARIOS.overcharge.similarity);
  const [historicalCustomer, setHistoricalCustomer] = useState(SAMPLE_SCENARIOS.overcharge.historicalCustomer);
  const [historicalSupport, setHistoricalSupport] = useState(SAMPLE_SCENARIOS.overcharge.historicalSupport);
  const [draftReply, setDraftReply] = useState(SAMPLE_SCENARIOS.overcharge.draftReply);
  const [action, setAction] = useState(SAMPLE_SCENARIOS.overcharge.action);
  const [reason, setReason] = useState(SAMPLE_SCENARIOS.overcharge.reason);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleLoadSample = (key) => {
    const sample = SAMPLE_SCENARIOS[key];
    if (!sample) return;
    setMessage(sample.message);
    setIntent(sample.intent);
    setConfidence(sample.confidence);
    setSimilarity(sample.similarity);
    setHistoricalCustomer(sample.historicalCustomer);
    setHistoricalSupport(sample.historicalSupport);
    setDraftReply(sample.draftReply);
    setAction(sample.action);
    setReason(sample.reason);
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Simulate UI processing for skeleton mode
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 450);
  };

  const handleToggleAction = (forcedAction) => {
    setAction(forcedAction);
    if (forcedAction === "AUTO_HANDLE") {
      setReason("A sufficiently similar historical resolution was found (similarity: 0.6210) with verified standard resolution steps.");
    } else {
      setReason("Historical responses indicate that this issue requires direct support follow-up.");
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
              Auditing log of recent inquiries and agent routing decisions. (Will populate once backend persistence is connected).
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
              Configurable routing rules: Similarity cutoff (default: 0.20), escalation keywords, and auto-dispatch policies.
            </p>
          </div>
        </div>
      );
    }

    // Default: Dashboard / New Conversation
    return (
      <div className="workspace-container">
        {/* Notice Banner */}
        <div className="notice-banner">
          <div className="notice-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
          </div>
          <div className="notice-content">
            <strong>Frontend UI Skeleton:</strong> Active visual placeholder mode. All UI cards, routing states, and controls are operational. Backend API integration connects in the next step.
          </div>
        </div>

        {/* 1. Customer Message Input Section */}
        <CustomerMessageCard
          message={message}
          setMessage={setMessage}
          onAnalyze={handleAnalyze}
          isAnalyzing={isAnalyzing}
          onLoadSample={handleLoadSample}
        />

        {/* 2. AI Analysis Section (3 Cards) */}
        <AnalysisCards
          intent={intent}
          confidence={confidence}
          similarity={similarity}
        />

        {/* Two-Column Responsive Layout for Details */}
        <div className="workspace-two-col">
          <div className="workspace-col-main">
            {/* 3. Draft Reply Section */}
            <DraftReplyCard
              draftReply={draftReply}
              setDraftReply={setDraftReply}
            />

            {/* 4. Historical Resolution Section */}
            <HistoricalResolutionCard
              historicalCustomer={historicalCustomer}
              historicalSupport={historicalSupport}
              similarity={similarity}
              intent={intent}
            />
          </div>

          <div className="workspace-col-side">
            {/* 5. Decision Section (AUTO_HANDLE vs ESCALATE) */}
            <DecisionCard
              action={action}
              reason={reason}
              onToggleAction={handleToggleAction}
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
        <Header />
        <main className="content-area">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
