import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

function ModelResponseItem({ model, response }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div 
      className="model-response" 
      onClick={() => setExpanded(!expanded)}
      style={{ cursor: 'pointer', transition: 'all 0.2s' }}
      title="Click to expand/collapse"
    >
      <h4>{model}</h4>
      <div style={{ fontSize: '0.85rem', color: '#475569', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>
        {expanded ? response : (response.length > 150 ? response.substring(0, 150) + "..." : response)}
      </div>
    </div>
  );
}

function ChatInterface({ conversation, onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  if (!conversation) {
    return (
      <div className="chat-interface">
        <div className="header">
          <h1>VERITAS <span>AI Verification & Trust Layer</span></h1>
        </div>
        <div className="messages-container" style={{ justifyContent: 'center', alignItems: 'center', color: '#64748b' }}>
          <h2>Select or create a conversation to begin</h2>
        </div>
      </div>
    );
  }

  const renderMessage = (msg, index) => {
    if (msg.role === 'user') {
      return (
        <div key={index} className="message user">
          <div className="message-bubble">{msg.content}</div>
        </div>
      );
    }

    const isComplete = !msg.loading?.stage1 && !msg.loading?.stage2 && !msg.loading?.stage3;
    const hasData = msg.stage1 || msg.stage2 || msg.stage3;

    if (!hasData) {
      return (
        <div key={index} className="message assistant">
          <div className="loading-indicator">
            <div className="spinner"></div> Initiating Verification Pipeline...
          </div>
        </div>
      );
    }

    return (
      <div key={index} className="message assistant">
        <div className="veritas-layout">
          {/* Main Area */}
          <div className="veritas-main">
            {msg.stage3?.response ? (
              <div className="verified-answer">
                <h3 style={{marginTop: 0, color: '#0f172a'}}>Verified Answer</h3>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>{msg.stage3.response}</div>
              </div>
            ) : (
              <div className="verified-answer" style={{display: 'flex', alignItems: 'center', gap: 12, color: '#64748b'}}>
                <div className="spinner"></div> Synthesizing verified response...
              </div>
            )}

            {/* Original Models Accordion / List */}
            {msg.stage1 && (
              <div className="models-panel">
                <div className="panel-title">Original Model Responses ({msg.stage1.length})</div>
                {msg.stage1.map((r, i) => (
                  <ModelResponseItem key={i} model={r.model} response={r.response} />
                ))}
              </div>
            )}
          </div>

          {/* Sidebar / Decision Card */}
          <div className="veritas-sidebar">
            {msg.metadata?.decision ? (
              <div className="decision-card">
                <div className="decision-header">
                  VERITAS DECISION
                  <span className={`status-badge status-${msg.metadata.decision.status}`}>
                    {msg.metadata.decision.status.replace('_', ' ')}
                  </span>
                </div>
                
                <div className="scores">
                  <div className="score-box">
                    <div className="label">Reliability</div>
                    <div className="value">{msg.metadata.decision.reliability_score}/100</div>
                  </div>
                  <div className="score-box">
                    <div className="label">Risk</div>
                    <div className="value">{msg.metadata.decision.risk_score}/100</div>
                  </div>
                </div>

                <div className="reasoning">
                  <strong>Why?</strong>
                  <ul>
                    {msg.metadata.decision.reasoning.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              </div>
            ) : (
              msg.loading?.stage2 && (
                <div className="decision-card" style={{justifyContent: 'center', alignItems: 'center', minHeight: 200, color: '#64748b'}}>
                  <div className="spinner"></div>
                  <div style={{marginTop: 12}}>Analyzing claims & risk...</div>
                </div>
              )
            )}

            {msg.metadata?.claims && msg.metadata.claims.length > 0 && (
              <div className="claims-panel">
                <div className="panel-title">Claim Verification</div>
                {msg.metadata.claims.map((c, i) => (
                  <div key={i} className="claim-item">
                    <div className="claim-header">
                      <div className="claim-text">{c.text}</div>
                      <div className={`claim-status ${c.status}`}>{c.status.replace('_', ' ')}</div>
                    </div>
                    <div style={{fontSize: '0.75rem', color: '#64748b'}}>
                      {c.supporting_models.length} model(s) support
                    </div>
                    <div className="claim-bar-container">
                      <div className="claim-bar-fill" style={{width: `${c.agreement_ratio * 100}%`}}></div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {msg.cost_metrics && (
              <div className="metrics-panel">
                <div className="panel-title">Control Plane</div>
                <div className="metrics-grid">
                  <div className="metric-item">
                    <span className="metric-label">Latency</span>
                    <span className="metric-value">{msg.cost_metrics.latency}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Estimated Cost</span>
                    <span className="metric-value">{msg.cost_metrics.estimated_cost}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Models</span>
                    <span className="metric-value">{msg.cost_metrics.models}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Verifications</span>
                    <span className="metric-value">{msg.cost_metrics.verification_calls}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="chat-interface">
      <div className="header">
        <h1>VERITAS <span>AI Verification & Trust Layer</span></h1>
      </div>

      <div className="messages-container">
        {conversation.messages.map((msg, index) => renderMessage(msg, index))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question to verify..."
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="verify-button"
            disabled={isLoading || !input.trim()}
          >
            Verify with Veritas
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatInterface;
