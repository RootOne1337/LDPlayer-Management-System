import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Workstations() {
  const [workstations, setWorkstations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedWs, setSelectedWs] = useState(null);

  useEffect(() => {
    fetchWorkstations();
    const interval = setInterval(fetchWorkstations, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchWorkstations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/workstations?skip=0&limit=100');
      setWorkstations(response.data || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && workstations.length === 0) {
    return <div style={styles.loading}>⏳ Loading workstations...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>🖥️ Workstations</h2>
        <button style={styles.addButton}>➕ Add Workstation</button>
      </div>

      {error && <div style={styles.error}>⚠️ {error}</div>}

      <div style={styles.grid}>
        {workstations.map(ws => (
          <div key={ws.id} style={styles.card}>
            <div style={styles.cardHeader}>
              <h3 style={styles.cardTitle}>{ws.name}</h3>
              <span style={styles.statusBadge(ws.status)}>
                {ws.status === 'ONLINE' ? '●' : '○'} {ws.status}
              </span>
            </div>
            <div style={styles.cardInfo}>
              <div>📍 {ws.ip_address}</div>
              <div>👤 {ws.username}</div>
              <div>🎮 {ws.emulators?.length || 0} emulators</div>
              <div>💾 {ws.disk_usage ? `${Math.round(ws.disk_usage)}%` : 'N/A'} disk</div>
            </div>
            <div style={styles.cardActions}>
              <button style={styles.actionBtn('primary')}>Refresh</button>
              <button style={styles.actionBtn('secondary')}>Details</button>
            </div>
          </div>
        ))}
      </div>

      {workstations.length === 0 && (
        <div style={styles.empty}>
          No workstations found. Add one to get started! ➕
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { padding: '2rem', maxWidth: '1400px', margin: '0 auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' },
  title: { fontSize: '2rem', fontWeight: 'bold', color: '#1a202c', margin: 0 },
  addButton: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '0.5rem',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: '500'
  },
  error: {
    background: '#fed7d7',
    color: '#742a2a',
    padding: '1rem',
    borderRadius: '0.5rem',
    marginBottom: '1rem'
  },
  loading: { textAlign: 'center', padding: '3rem', color: '#666' },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem'
  },
  card: {
    background: 'white',
    padding: '1.5rem',
    borderRadius: '0.75rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    transition: 'all 0.3s ease',
    cursor: 'pointer'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
    borderBottom: '1px solid #e2e8f0',
    paddingBottom: '0.75rem'
  },
  cardTitle: { fontSize: '1.25rem', fontWeight: 'bold', margin: 0, color: '#1a202c' },
  statusBadge: (status) => ({
    padding: '0.35rem 0.75rem',
    borderRadius: '0.25rem',
    fontSize: '0.8rem',
    fontWeight: '500',
    background: status === 'ONLINE' ? '#c6f6d5' : '#fed7d7',
    color: status === 'ONLINE' ? '#22543d' : '#742a2a'
  }),
  cardInfo: { fontSize: '0.9rem', color: '#4a5568', lineHeight: '1.8rem', marginBottom: '1rem' },
  cardActions: {
    display: 'flex',
    gap: '0.5rem',
    justifyContent: 'flex-end'
  },
  actionBtn: (type) => ({
    padding: '0.5rem 1rem',
    border: type === 'primary' ? 'none' : '1px solid #cbd5e0',
    background: type === 'primary' ? '#667eea' : 'white',
    color: type === 'primary' ? 'white' : '#667eea',
    borderRadius: '0.35rem',
    cursor: 'pointer',
    fontSize: '0.85rem',
    fontWeight: '500'
  }),
  empty: {
    textAlign: 'center',
    padding: '3rem',
    color: '#a0aec0',
    fontSize: '1.1rem'
  }
};
