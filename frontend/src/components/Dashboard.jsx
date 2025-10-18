import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const data = await api.getSystemStatus();
      setStatus(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={styles.loading}>⏳ Loading system status...</div>;
  }

  if (error) {
    return <div style={styles.error}>❌ Error: {error}</div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📊 System Dashboard</h2>
      
      <div style={styles.grid}>
        {/* Status Card */}
        <div style={{...styles.card, ...styles.statusCard}}>
          <div style={styles.cardIcon}>✅</div>
          <div style={styles.cardTitle}>System Status</div>
          <div style={styles.cardValue}>{status?.status || 'Unknown'}</div>
          <div style={styles.cardSubtitle}>Version {status?.version || '1.0.0'}</div>
        </div>

        {/* Workstations Card */}
        <div style={{...styles.card, ...styles.workstationCard}}>
          <div style={styles.cardIcon}>🖥️</div>
          <div style={styles.cardTitle}>Workstations</div>
          <div style={styles.cardValue}>{status?.connected_workstations || 0}</div>
          <div style={styles.cardSubtitle}>Connected</div>
        </div>

        {/* Emulators Card */}
        <div style={{...styles.card, ...styles.emulatorCard}}>
          <div style={styles.cardIcon}>🎮</div>
          <div style={styles.cardTitle}>Emulators</div>
          <div style={styles.cardValue}>{status?.total_emulators || 0}</div>
          <div style={styles.cardSubtitle}>Total</div>
        </div>

        {/* Operations Card */}
        <div style={{...styles.card, ...styles.operationCard}}>
          <div style={styles.cardIcon}>⚙️</div>
          <div style={styles.cardTitle}>Operations</div>
          <div style={styles.cardValue}>{status?.active_operations || 0}</div>
          <div style={styles.cardSubtitle}>Active</div>
        </div>
      </div>

      {/* System Info */}
      <div style={styles.infoCard}>
        <h3 style={styles.infoTitle}>🕐 System Information</h3>
        <div style={styles.infoGrid}>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Uptime:</span>
            <span style={styles.infoValue}>{status?.uptime || 'N/A'}</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Last Update:</span>
            <span style={styles.infoValue}>
              {status?.timestamp ? new Date(status.timestamp).toLocaleTimeString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '30px'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    textAlign: 'center',
    transition: 'transform 0.2s, box-shadow 0.2s'
  },
  statusCard: {
    borderTop: '4px solid #48bb78'
  },
  workstationCard: {
    borderTop: '4px solid #4299e1'
  },
  emulatorCard: {
    borderTop: '4px solid #ed8936'
  },
  operationCard: {
    borderTop: '4px solid #9f7aea'
  },
  cardIcon: {
    fontSize: '48px',
    marginBottom: '12px'
  },
  cardTitle: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '8px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  cardValue: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '4px'
  },
  cardSubtitle: {
    fontSize: '12px',
    color: '#999'
  },
  infoCard: {
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
  },
  infoTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '20px'
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px'
  },
  infoItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px',
    background: '#f7fafc',
    borderRadius: '8px'
  },
  infoLabel: {
    fontWeight: '600',
    color: '#666'
  },
  infoValue: {
    color: '#333'
  },
  loading: {
    textAlign: 'center',
    padding: '60px',
    fontSize: '18px',
    color: '#666'
  },
  error: {
    textAlign: 'center',
    padding: '60px',
    fontSize: '18px',
    color: '#c33',
    background: '#fee',
    borderRadius: '12px',
    margin: '20px'
  }
};
