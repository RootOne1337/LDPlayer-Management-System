import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Operations() {
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOperations();
    const interval = setInterval(fetchOperations, 3000); // Real-time updates
    return () => clearInterval(interval);
  }, []);

  const fetchOperations = async () => {
    try {
      const response = await api.get('/api/operations?skip=0&limit=50');
      setOperations(response.data || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'SUCCESS': return '#22543d';
      case 'FAILED': return '#742a2a';
      case 'RUNNING': return '#153e75';
      case 'PENDING': return '#7c2d12';
      default: return '#4a5568';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'SUCCESS': return '#c6f6d5';
      case 'FAILED': return '#fed7d7';
      case 'RUNNING': return '#bee3f8';
      case 'PENDING': return '#fed7aa';
      default: return '#edf2f7';
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📋 Operations Log</h2>

      {error && <div style={styles.error}>⚠️ {error}</div>}

      {loading && operations.length === 0 ? (
        <div style={styles.loading}>⏳ Loading operations...</div>
      ) : (
        <div style={styles.table}>
          <div style={styles.tableHeader}>
            <div style={{ flex: 2 }}>Operation</div>
            <div style={{ flex: 1 }}>Resource</div>
            <div style={{ flex: 1 }}>Status</div>
            <div style={{ flex: 1 }}>Progress</div>
            <div style={{ flex: 1 }}>Time</div>
          </div>

          {operations.map(op => (
            <div key={op.id} style={styles.tableRow}>
              <div style={{ flex: 2, fontWeight: '500' }}>{op.operation_type}</div>
              <div style={{ flex: 1, color: '#666' }}>
                {op.workstation_id || op.emulator_id || 'N/A'}
              </div>
              <div style={{ flex: 1 }}>
                <span style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: '0.25rem',
                  fontSize: '0.8rem',
                  fontWeight: '500',
                  background: getStatusBg(op.status),
                  color: getStatusColor(op.status)
                }}>
                  {op.status}
                </span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={styles.progressBar}>
                  <div style={{
                    ...styles.progressFill,
                    width: `${op.progress || 0}%`,
                    background: op.status === 'SUCCESS' ? '#48bb78' : 
                               op.status === 'FAILED' ? '#f56565' : '#4299e1'
                  }} />
                </div>
                {op.progress}%
              </div>
              <div style={{ flex: 1, color: '#999', fontSize: '0.85rem' }}>
                {new Date(op.created_at).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {operations.length === 0 && !loading && (
        <div style={styles.empty}>
          No operations recorded yet. Start managing your emulators! 🚀
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { padding: '2rem', maxWidth: '1400px', margin: '0 auto' },
  title: { fontSize: '2rem', fontWeight: 'bold', marginBottom: '2rem', color: '#1a202c' },
  error: {
    background: '#fed7d7',
    color: '#742a2a',
    padding: '1rem',
    borderRadius: '0.5rem',
    marginBottom: '1rem'
  },
  loading: { textAlign: 'center', padding: '3rem', color: '#666' },
  table: {
    background: 'white',
    borderRadius: '0.75rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    overflow: 'hidden'
  },
  tableHeader: {
    display: 'flex',
    padding: '1rem',
    background: '#f7fafc',
    fontWeight: '600',
    borderBottom: '2px solid #e2e8f0',
    fontSize: '0.9rem'
  },
  tableRow: {
    display: 'flex',
    padding: '1rem',
    borderBottom: '1px solid #e2e8f0',
    alignItems: 'center',
    fontSize: '0.9rem'
  },
  progressBar: {
    width: '100%',
    height: '6px',
    background: '#e2e8f0',
    borderRadius: '3px',
    overflow: 'hidden',
    marginBottom: '0.25rem'
  },
  progressFill: {
    height: '100%',
    transition: 'width 0.3s ease'
  },
  empty: {
    textAlign: 'center',
    padding: '3rem',
    color: '#a0aec0'
  }
};
