import { useState, useEffect } from 'react';
import './Sidebar.css';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>VERITAS</h1>
        <button className="new-conversation-btn" onClick={onNewConversation}>
          + New Verification
        </button>
      </div>

      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div className="no-conversations">No verifications yet</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${
                conv.id === currentConversationId ? 'active' : ''
              }`}
              onClick={() => onSelectConversation(conv.id)}
              style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <div style={{flex: 1, overflow: 'hidden'}}>
                <div className="conversation-title" style={{ whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                  {conv.title || 'New Verification'}
                </div>
                <div className="conversation-meta">
                  {conv.message_count} messages
                </div>
              </div>
              
              <button 
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  if(window.confirm('Delete this conversation?')) {
                    onDeleteConversation(conv.id);
                  }
                }}
                style={{
                  background: 'transparent', 
                  border: 'none', 
                  color: '#94a3b8', 
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '4px'
                }}
                title="Delete Conversation"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
